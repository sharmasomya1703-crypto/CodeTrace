from __future__ import annotations

from typing import Any


def replay_array_events(initial: list[Any], events: list[dict[str, Any]]) -> list[Any]:
    """Replay mutating array events to reconstruct final state."""
    data = list(initial)
    for ev in events:
        t = ev.get("type")
        if t == "swap":
            i, j = ev["indices"]
            data[i], data[j] = data[j], data[i]
        elif t == "overwrite":
            data[ev["index"]] = ev["value"]
    return data


def count_event_types(events: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for ev in events:
        t = ev.get("type", "unknown")
        counts[t] = counts.get(t, 0) + 1
    return counts
