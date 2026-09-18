from __future__ import annotations

from codetrace.events.models import AlgorithmResult


def merge_sort(arr: list[int]) -> AlgorithmResult:
    data = list(arr)
    events: list[dict] = []
    comparisons = writes = 0

    def merge(left: int, mid: int, right: int) -> None:
        nonlocal comparisons, writes
        left_part = data[left : mid + 1]
        right_part = data[mid + 1 : right + 1]
        i = j = 0
        k = left
        while i < len(left_part) and j < len(right_part):
            comparisons += 1
            events.append(
                {
                    "type": "compare",
                    "indices": [left + i, mid + 1 + j],
                    "values": [left_part[i], right_part[j]],
                }
            )
            if left_part[i] <= right_part[j]:
                writes += 1
                events.append(
                    {
                        "type": "overwrite",
                        "index": k,
                        "value": left_part[i],
                        "previous": data[k],
                    }
                )
                data[k] = left_part[i]
                i += 1
            else:
                writes += 1
                events.append(
                    {
                        "type": "overwrite",
                        "index": k,
                        "value": right_part[j],
                        "previous": data[k],
                    }
                )
                data[k] = right_part[j]
                j += 1
            k += 1
        while i < len(left_part):
            writes += 1
            events.append(
                {
                    "type": "overwrite",
                    "index": k,
                    "value": left_part[i],
                    "previous": data[k],
                }
            )
            data[k] = left_part[i]
            i += 1
            k += 1
        while j < len(right_part):
            writes += 1
            events.append(
                {
                    "type": "overwrite",
                    "index": k,
                    "value": right_part[j],
                    "previous": data[k],
                }
            )
            data[k] = right_part[j]
            j += 1
            k += 1

    def sort_range(left: int, right: int) -> None:
        if left >= right:
            return
        mid = (left + right) // 2
        sort_range(left, mid)
        sort_range(mid + 1, right)
        merge(left, mid, right)

    if data:
        sort_range(0, len(data) - 1)
    metrics = {"comparisons": comparisons, "swaps": 0, "writes": writes, "visited": 0}
    events.append({"type": "complete", "result": list(data), "metrics": metrics})
    return AlgorithmResult(
        algorithm="merge-sort",
        input=list(arr),
        events=events,
        result=list(data),
        metrics=metrics,
    )
