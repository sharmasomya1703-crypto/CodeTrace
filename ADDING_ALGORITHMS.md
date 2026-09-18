# Adding Algorithms

## Backend (source of truth)

1. Create `backend/codetrace/algorithms/<name>.py`.
2. Implement a function that accepts input and returns an `AlgorithmResult`:

```python
from codetrace.events.models import AlgorithmResult, Event

def bubble_sort(arr: list[int]) -> AlgorithmResult:
    data = list(arr)
    events: list[Event] = []
    comparisons = swaps = 0
    # ... emit compare / swap events ...
    events.append({"type": "complete", "result": list(data), "metrics": {...}})
    return AlgorithmResult(
        algorithm="bubble-sort",
        input=list(arr),
        events=events,
        result=list(data),
        metrics={"comparisons": comparisons, "swaps": swaps, "writes": 0, "visited": 0},
    )
```

3. Register metadata in `algorithms/registry.py` (id, title, category, complexities, explanation).
4. Add tests in `backend/tests/test_algorithms_*.py`:

   - Final output correctness
   - Event validity
   - Replay equals final state
   - Deterministic metrics for fixed input

5. Update `ALGORITHM_EVENTS.md` if you introduce a new event type.

## Frontend

1. Add display metadata if not fetched from API (`frontend/src/algorithms/meta.ts`).
2. Ensure the correct visualizer (array vs graph) is selected by category.
3. Prefer generating steps via API or worker — do not re-implement logic in React components.

## Checklist

- [ ] Pure function, no UI imports
- [ ] Emits `complete` as the last event
- [ ] Metrics match event counts where applicable
- [ ] Unit tests cover empty / single / duplicates / larger inputs
- [ ] Explanation fields filled for the library page
