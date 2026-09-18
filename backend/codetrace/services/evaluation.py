from __future__ import annotations

import os
from typing import Any

from codetrace.problems.registry import get_problem_full, list_problems
from codetrace.runners.base import ResourceLimits
from codetrace.runners.subprocess_runner import get_runner
from codetrace.scoring.engine import score_execution


def evaluate_solution(problem_id: str, source: str) -> dict[str, Any]:
    if os.environ.get("CODETRACE_ENABLE_EVAL", "true").lower() in {"0", "false", "no"}:
        return {
            "ok": False,
            "error": "Evaluation is disabled by configuration (CODETRACE_ENABLE_EVAL).",
        }

    try:
        problem = get_problem_full(problem_id)
    except KeyError as exc:
        return {"ok": False, "error": str(exc)}

    if not source or not source.strip():
        return {"ok": False, "error": "Empty solution source"}

    # Reject obviously huge or binary-looking payloads early
    if "\x00" in source:
        return {"ok": False, "error": "Malformed solution file"}

    runner_name = os.environ.get("CODETRACE_RUNNER", "subprocess")
    runner = get_runner(runner_name)
    timeout = float(
        os.environ.get("CODETRACE_DEFAULT_TIMEOUT", problem.get("timeout_seconds", 2.0))
    )
    max_out = int(os.environ.get("CODETRACE_MAX_OUTPUT_BYTES", "64000"))
    limits = ResourceLimits(timeout_seconds=timeout, max_output_bytes=max_out)

    result = runner.run(source, problem, limits)
    scores = score_execution(result)

    visible = []
    hidden_summary = {"passed": 0, "failed": 0, "total": 0}
    for outcome in result.outcomes:
        if outcome.hidden:
            hidden_summary["total"] += 1
            if outcome.passed and not outcome.timed_out:
                hidden_summary["passed"] += 1
            else:
                hidden_summary["failed"] += 1
        else:
            visible.append(
                {
                    "test_id": outcome.test_id,
                    "passed": outcome.passed,
                    "runtime_ms": round(outcome.runtime_ms, 4),
                    "timed_out": outcome.timed_out,
                    "exception": outcome.exception,
                    "expected": outcome.expected,
                    "actual": outcome.actual,
                    "is_edge_case": outcome.is_edge_case,
                }
            )

    return {
        "ok": True,
        "problem_id": problem_id,
        "success": result.success and not result.timed_out,
        "timed_out": result.timed_out,
        "error": result.error,
        "wall_time_ms": round(result.wall_time_ms, 4),
        "scores": {
            "correctness": scores.correctness,
            "edge_cases": scores.edge_cases,
            "performance": scores.performance,
            "overall": scores.overall,
            "weights": scores.weights,
        },
        "visible_tests": visible,
        "hidden_summary": hidden_summary,
        "security_note": (
            "Executed via subprocess isolation outside the API process. "
            "This is not a complete security sandbox."
        ),
    }


def problems_catalog() -> list[dict[str, Any]]:
    return list_problems()
