from __future__ import annotations

from codetrace.events.models import AlgorithmResult


def quick_sort(arr: list[int]) -> AlgorithmResult:
    data = list(arr)
    events: list[dict] = []
    comparisons = swaps = 0

    def partition(low: int, high: int) -> int:
        nonlocal comparisons, swaps
        pivot = data[high]
        events.append({"type": "highlight", "index": high, "role": "pivot"})
        i = low
        for j in range(low, high):
            comparisons += 1
            events.append(
                {
                    "type": "compare",
                    "indices": [j, high],
                    "values": [data[j], pivot],
                }
            )
            if data[j] <= pivot:
                if i != j:
                    data[i], data[j] = data[j], data[i]
                    swaps += 1
                    events.append(
                        {
                            "type": "swap",
                            "indices": [i, j],
                            "values": [data[i], data[j]],
                        }
                    )
                i += 1
        if i != high:
            data[i], data[high] = data[high], data[i]
            swaps += 1
            events.append(
                {
                    "type": "swap",
                    "indices": [i, high],
                    "values": [data[i], data[high]],
                }
            )
        return i

    def sort_range(low: int, high: int) -> None:
        if low >= high:
            return
        p = partition(low, high)
        sort_range(low, p - 1)
        sort_range(p + 1, high)

    if data:
        sort_range(0, len(data) - 1)
    metrics = {"comparisons": comparisons, "swaps": swaps, "writes": 0, "visited": 0}
    events.append({"type": "complete", "result": list(data), "metrics": metrics})
    return AlgorithmResult(
        algorithm="quick-sort",
        input=list(arr),
        events=events,
        result=list(data),
        metrics=metrics,
    )
