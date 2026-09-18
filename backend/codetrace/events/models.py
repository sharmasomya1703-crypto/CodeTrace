from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Event(BaseModel):
    """Structured visualization event. Extra fields allowed for forward compatibility."""

    type: str
    model_config = {"extra": "allow"}


class Metrics(BaseModel):
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0
    visited: int = 0
    enqueues: int = 0
    relaxations: int = 0


class AlgorithmResult(BaseModel):
    algorithm: str
    input: Any
    events: list[dict[str, Any]] = Field(default_factory=list)
    result: Any = None
    metrics: dict[str, int] = Field(default_factory=dict)


ALLOWED_EVENT_TYPES = frozenset(
    {
        "compare",
        "swap",
        "overwrite",
        "visit",
        "enqueue",
        "dequeue",
        "push",
        "pop",
        "relax_edge",
        "highlight",
        "found",
        "not_found",
        "set_key",
        "complete",
    }
)


def validate_events(events: list[dict[str, Any]]) -> list[str]:
    """Return a list of validation error strings (empty if OK)."""
    errors: list[str] = []
    if not events:
        errors.append("event list is empty")
        return errors
    if events[-1].get("type") != "complete":
        errors.append("last event must be complete")
    for i, ev in enumerate(events):
        t = ev.get("type")
        if not t:
            errors.append(f"event[{i}] missing type")
        elif t not in ALLOWED_EVENT_TYPES:
            errors.append(f"event[{i}] unknown type: {t}")
    return errors
