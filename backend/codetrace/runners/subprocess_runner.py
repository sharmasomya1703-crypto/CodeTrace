from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from codetrace.runners.base import ExecutionResult, ResourceLimits, Runner, TestOutcome

HARNESS_TEMPLATE = r'''
import json
import sys
import time
import traceback

RESULTS = []

def deep_equal(a, b):
    return a == b

def run_one(test):
    started = time.perf_counter()
    try:
        import solution as sol
        fn = getattr(sol, FUNCTION_NAME)
        args = test.get("args") or []
        kwargs = test.get("kwargs") or {}
        actual = fn(*args, **kwargs)
        expected = test.get("expected")
        passed = deep_equal(actual, expected)
        RESULTS.append({
            "test_id": test["id"],
            "passed": passed,
            "runtime_ms": (time.perf_counter() - started) * 1000.0,
            "timed_out": False,
            "exception": None,
            "expected": expected,
            "actual": actual,
            "is_edge_case": bool(test.get("is_edge_case", False)),
            "performance_weight": float(test.get("performance_weight", 0) or 0),
            "hidden": bool(test.get("hidden", False)),
            "stderr": "",
        })
    except Exception as exc:
        RESULTS.append({
            "test_id": test["id"],
            "passed": False,
            "runtime_ms": (time.perf_counter() - started) * 1000.0,
            "timed_out": False,
            "exception": f"{type(exc).__name__}: {exc}",
            "expected": test.get("expected"),
            "actual": None,
            "is_edge_case": bool(test.get("is_edge_case", False)),
            "performance_weight": float(test.get("performance_weight", 0) or 0),
            "hidden": bool(test.get("hidden", False)),
            "stderr": traceback.format_exc(),
        })

def main():
    global FUNCTION_NAME
    payload = json.loads(sys.stdin.read())
    FUNCTION_NAME = payload["function_name"]
    for test in payload["tests"]:
        run_one(test)
    print("___CODETRACE_RESULTS___")
    print(json.dumps(RESULTS))

if __name__ == "__main__":
    main()
'''


class SubprocessLocalRunner(Runner):
    """
    Runs student code in a separate Python process.

    This is NOT a complete security sandbox. See RUNNER_SECURITY.md.
    """

    def run(
        self,
        solution_source: str,
        problem: dict[str, Any],
        limits: ResourceLimits,
    ) -> ExecutionResult:
        tmp = Path(tempfile.mkdtemp(prefix="codetrace_"))
        started = time.perf_counter()
        try:
            (tmp / "solution.py").write_text(solution_source, encoding="utf-8")
            (tmp / "harness.py").write_text(HARNESS_TEMPLATE, encoding="utf-8")

            tests = []
            for t in problem.get("visible_tests", []):
                item = dict(t)
                item["hidden"] = False
                tests.append(item)
            for t in problem.get("hidden_tests", []):
                item = dict(t)
                item["hidden"] = True
                tests.append(item)

            payload = {
                "function_name": problem["function_name"],
                "tests": tests,
            }
            payload_bytes = json.dumps(payload).encode("utf-8")
            if len(payload_bytes) > limits.max_output_bytes * 4:
                return ExecutionResult(
                    success=False,
                    error="Input payload too large",
                    wall_time_ms=(time.perf_counter() - started) * 1000,
                )

            env = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": str(tmp),
                "PYTHONIOENCODING": "utf-8",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            # Strip potentially sensitive vars
            for key in ("HOME", "USERPROFILE", "USERNAME"):
                if key in os.environ:
                    env[key] = os.environ[key]

            preexec = None
            if hasattr(os, "setuid") and sys.platform != "win32":
                try:
                    import resource

                    def _limits() -> None:
                        if limits.max_memory_mb:
                            mem = limits.max_memory_mb * 1024 * 1024
                            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                        # CPU seconds soft/hard
                        cpu = max(1, int(limits.timeout_seconds) + 1)
                        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))

                    preexec = _limits
                except Exception:
                    preexec = None

            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]

            proc = subprocess.Popen(
                [sys.executable, str(tmp / "harness.py")],
                cwd=str(tmp),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                shell=False,
                preexec_fn=preexec,
                creationflags=creationflags,
            )
            timed_out = False
            try:
                stdout_b, stderr_b = proc.communicate(
                    input=payload_bytes,
                    timeout=limits.timeout_seconds * max(1, len(tests)) + 1,
                )
            except subprocess.TimeoutExpired:
                timed_out = True
                _terminate(proc)
                stdout_b, stderr_b = proc.communicate(timeout=2)

            stdout = _clip(stdout_b.decode("utf-8", errors="replace"), limits.max_output_bytes)
            stderr = _clip(stderr_b.decode("utf-8", errors="replace"), limits.max_output_bytes)

            if timed_out:
                outcomes = [
                    TestOutcome(
                        test_id=t["id"],
                        passed=False,
                        runtime_ms=limits.timeout_seconds * 1000,
                        timed_out=True,
                        exception="Timeout",
                        expected=None if t.get("hidden") else t.get("expected"),
                        actual=None,
                        is_edge_case=bool(t.get("is_edge_case", False)),
                        performance_weight=float(t.get("performance_weight", 0) or 0),
                        hidden=bool(t.get("hidden", False)),
                    )
                    for t in tests
                ]
                return ExecutionResult(
                    success=False,
                    outcomes=outcomes,
                    stdout=stdout,
                    stderr=stderr,
                    error="Execution timed out",
                    timed_out=True,
                    wall_time_ms=(time.perf_counter() - started) * 1000,
                )

            if len(stdout_b) > limits.max_output_bytes or len(stderr_b) > limits.max_output_bytes:
                return ExecutionResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr,
                    error="Excessive output",
                    wall_time_ms=(time.perf_counter() - started) * 1000,
                )

            outcomes = _parse_outcomes(stdout, tests)
            if outcomes is None:
                return ExecutionResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr,
                    error="Malformed harness output or solution crash",
                    wall_time_ms=(time.perf_counter() - started) * 1000,
                )

            return ExecutionResult(
                success=True,
                outcomes=outcomes,
                stdout=stdout,
                stderr=stderr,
                wall_time_ms=(time.perf_counter() - started) * 1000,
            )
        except Exception as exc:
            return ExecutionResult(
                success=False,
                error=f"Runner failure: {exc}",
                wall_time_ms=(time.perf_counter() - started) * 1000,
            )
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def _terminate(proc: subprocess.Popen[bytes]) -> None:
    try:
        proc.kill()
    except Exception:
        pass


def _clip(text: str, limit: int) -> str:
    if len(text.encode("utf-8", errors="replace")) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def _parse_outcomes(stdout: str, tests: list[dict[str, Any]]) -> list[TestOutcome] | None:
    marker = "___CODETRACE_RESULTS___"
    if marker not in stdout:
        return None
    raw = stdout.split(marker, 1)[1].strip().splitlines()
    if not raw:
        return None
    try:
        data = json.loads(raw[0])
    except json.JSONDecodeError:
        return None
    by_id = {item["test_id"]: item for item in data}
    outcomes: list[TestOutcome] = []
    for t in tests:
        item = by_id.get(t["id"])
        hidden = bool(t.get("hidden", False))
        if not item:
            outcomes.append(
                TestOutcome(
                    test_id=t["id"],
                    passed=False,
                    runtime_ms=0,
                    exception="Missing result",
                    hidden=hidden,
                    is_edge_case=bool(t.get("is_edge_case", False)),
                    performance_weight=float(t.get("performance_weight", 0) or 0),
                )
            )
            continue
        expected = item.get("expected")
        actual = item.get("actual")
        if hidden:
            expected = None
            actual = None
        outcomes.append(
            TestOutcome(
                test_id=item["test_id"],
                passed=bool(item.get("passed")),
                runtime_ms=float(item.get("runtime_ms") or 0),
                timed_out=bool(item.get("timed_out")),
                exception=item.get("exception"),
                expected=expected,
                actual=actual,
                is_edge_case=bool(item.get("is_edge_case", False)),
                performance_weight=float(item.get("performance_weight", 0) or 0),
                hidden=hidden,
                stderr=item.get("stderr") or "",
            )
        )
    return outcomes


class DockerRunner(Runner):
    """Placeholder for future Docker-based isolation."""

    def run(
        self,
        solution_source: str,
        problem: dict[str, Any],
        limits: ResourceLimits,
    ) -> ExecutionResult:
        return ExecutionResult(
            success=False,
            error="DockerRunner is not implemented yet. Use SubprocessLocalRunner.",
        )


def get_runner(name: str = "subprocess") -> Runner:
    if name == "subprocess":
        return SubprocessLocalRunner()
    if name == "docker":
        return DockerRunner()
    raise ValueError(f"Unknown runner: {name}")
