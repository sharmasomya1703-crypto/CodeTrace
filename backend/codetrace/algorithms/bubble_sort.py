from __future__ import annotations

from codetrace.events.models import AlgorithmResult


def bubble_sort(arr: list[int]) -> AlgorithmResult:
    data = list(arr)
    events: list[dict] = []
    comparisons = swaps = 0
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            comparisons += 1
            events.append(
                {
                    "type": "compare",
                    "indices": [j, j + 1],
                    "values": [data[j], data[j + 1]],
                }
            )
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swaps += 1
                swapped = True
                events.append(
                    {
                        "type": "swap",
                        "indices": [j, j + 1],
                        "values": [data[j], data[j + 1]],
                    }
                )
        events.append(
            {
                "type": "highlight",
                "indices": list(range(n - i - 1, n)),
                "role": "sorted",
            }
        )
        if not swapped:
            break
    metrics = {"comparisons": comparisons, "swaps": swaps, "writes": 0, "visited": 0}
    events.append({"type": "complete", "result": list(data), "metrics": metrics})
    return AlgorithmResult(
        algorithm="bubble-sort",
        input=list(arr),
        events=events,
        result=list(data),
        metrics=metrics,
    )
