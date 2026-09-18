from __future__ import annotations

from codetrace.events.models import AlgorithmResult


def binary_search(arr: list[int], target: int) -> AlgorithmResult:
    data = list(arr)
    events: list[dict] = []
    comparisons = visited = 0
    low, high = 0, len(data) - 1
    found_index = -1
    while low <= high:
        mid = (low + high) // 2
        visited += 1
        events.append({"type": "visit", "index": mid, "value": data[mid], "structure": "array"})
        events.append(
            {
                "type": "highlight",
                "indices": list(range(low, high + 1)),
                "role": "search_range",
            }
        )
        comparisons += 1
        events.append(
            {
                "type": "compare",
                "indices": [mid],
                "values": [data[mid], target],
            }
        )
        if data[mid] == target:
            found_index = mid
            events.append({"type": "found", "index": mid, "value": data[mid]})
            break
        if data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
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
        algorithm="binary-search",
        input={"array": data, "target": target},
        events=events,
        result=found_index,
        metrics=metrics,
    )
