from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def list_problems() -> list[dict[str, Any]]:
    problems = []
    for path in sorted(DATA_DIR.glob("*.json")):
        problem = _load(path)
        problems.append(public_view(problem))
    return problems


def get_problem(problem_id: str, *, include_hidden: bool = False) -> dict[str, Any]:
    path = DATA_DIR / f"{problem_id}.json"
    if not path.exists():
        raise KeyError(f"Unknown problem: {problem_id}")
    problem = _load(path)
    if include_hidden:
        return problem
    return public_view(problem)


def public_view(problem: dict[str, Any]) -> dict[str, Any]:
    """Strip hidden test inputs/expected for API/CLI show."""
    return {
        "id": problem["id"],
        "title": problem["title"],
        "description": problem["description"],
        "function_name": problem["function_name"],
        "signature": problem["signature"],
        "constraints": problem.get("constraints", []),
        "timeout_seconds": problem.get("timeout_seconds", 2.0),
        "expected_output_format": problem.get("expected_output_format", ""),
        "visible_tests": problem.get("visible_tests", []),
        "hidden_test_count": len(problem.get("hidden_tests", [])),
    }


def get_problem_full(problem_id: str) -> dict[str, Any]:
    return get_problem(problem_id, include_hidden=True)
