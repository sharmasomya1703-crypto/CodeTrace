from __future__ import annotations

from dataclasses import dataclass

from codetrace.runners.base import ExecutionResult


@dataclass
class ScoreBreakdown:
    correctness: float
    edge_cases: float
    performance: float
    overall: float
    weights: dict[str, float]


DEFAULT_WEIGHTS = {
    "correctness": 0.70,
    "edge_cases": 0.20,
    "performance": 0.10,
}


def score_execution(
    result: ExecutionResult,
    weights: dict[str, float] | None = None,
) -> ScoreBreakdown:
    """
    Deterministic scoring from real test outcomes.

    - Correctness: fraction of all non-performance-only tests passed
    - Edge cases: fraction of is_edge_case tests passed (100 if none)
    - Performance: fraction of performance_weight tests passed under no timeout
    """
    w = dict(DEFAULT_WEIGHTS if weights is None else weights)
    outcomes = result.outcomes
    if not outcomes:
        return ScoreBreakdown(0.0, 0.0, 0.0, 0.0, w)

    all_tests = outcomes
    correctness = _ratio(all_tests)

    edge = [o for o in outcomes if o.is_edge_case]
    edge_score = _ratio(edge) if edge else 1.0

    perf = [o for o in outcomes if o.performance_weight > 0]
    if not perf:
        perf_score = 1.0
    else:
        # Weighted by performance_weight; timeouts count as fail
        total_w = sum(o.performance_weight for o in perf) or 1.0
        gained = sum(o.performance_weight for o in perf if o.passed and not o.timed_out)
        perf_score = gained / total_w

    overall = (
        correctness * w["correctness"]
        + edge_score * w["edge_cases"]
        + perf_score * w["performance"]
    )
    return ScoreBreakdown(
        correctness=round(correctness * 100, 2),
        edge_cases=round(edge_score * 100, 2),
        performance=round(perf_score * 100, 2),
        overall=round(overall * 100, 2),
        weights=w,
    )


def _ratio(outcomes: list) -> float:
    if not outcomes:
        return 0.0
    return sum(1 for o in outcomes if o.passed and not o.timed_out) / len(outcomes)
