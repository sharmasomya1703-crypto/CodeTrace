from __future__ import annotations

from codetrace.events.models import AlgorithmResult


def linear_search(arr: list[int], target: int) -> AlgorithmResult:
    data = list(arr)
    events: list[dict] = []
    comparisons = visited = 0
    found_index = -1
    for i, value in enumerate(data):
        comparisons += 1
        visited += 1
        events.append({"type": "compare", "indices": [i], "values": [value, target]})
        events.append({"type": "visit", "index": i, "value": value, "structure": "array"})
        if value == target:
            found_index = i
            events.append({"type": "found", "index": i, "value": value})
            break
    if found_index < 0:
        events.append({"type": "not_found", "target": target})
    metrics = {
        "comparisons": comparisons,
        "swaps": 0,
        "writes": 0,
        "visited": visited,
    }
    events.append({"type": "complete", "result": found_index, "metrics": metrics})
    return AlgorithmResult(
        algorithm="linear-search",
        input={"array": data, "target": target},
        events=events,
        result=found_index,
        metrics=metrics,
    )
