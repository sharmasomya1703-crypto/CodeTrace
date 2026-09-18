from __future__ import annotations

from codetrace.events.models import AlgorithmResult


def insertion_sort(arr: list[int]) -> AlgorithmResult:
    data = list(arr)
    events: list[dict] = []
    comparisons = writes = 0
    for i in range(1, len(data)):
        key = data[i]
        events.append({"type": "set_key", "index": i, "value": key})
        j = i - 1
        while j >= 0:
            comparisons += 1
            events.append(
                {
                    "type": "compare",
                    "indices": [j, i],
                    "values": [data[j], key],
                }
            )
            if data[j] <= key:
                break
            writes += 1
            events.append(
                {
                    "type": "overwrite",
                    "index": j + 1,
                    "value": data[j],
                    "previous": data[j + 1],
                }
            )
            data[j + 1] = data[j]
            j -= 1
        writes += 1
        events.append(
            {
                "type": "overwrite",
                "index": j + 1,
                "value": key,
                "previous": data[j + 1],
            }
        )
        data[j + 1] = key
        events.append({"type": "highlight", "indices": list(range(i + 1)), "role": "sorted"})
    metrics = {"comparisons": comparisons, "swaps": 0, "writes": writes, "visited": 0}
    events.append({"type": "complete", "result": list(data), "metrics": metrics})
    return AlgorithmResult(
        algorithm="insertion-sort",
        input=list(arr),
        events=events,
        result=list(data),
        metrics=metrics,
    )
