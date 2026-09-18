# Problem Format

Evaluation problems are declarative JSON (or Python dict) definitions loaded by the problem registry.

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable slug, e.g. `binary-search` |
| `title` | string | Human-readable name |
| `description` | string | Problem statement (Markdown allowed) |
| `function_name` | string | Entry function students must define |
| `signature` | string | Display signature, e.g. `def binary_search(arr: list[int], target: int) -> int` |
| `constraints` | list[string] | Informal constraints for students |
| `timeout_seconds` | number | Per-test wall-clock timeout |
| `visible_tests` | list[TestCase] | Shown to the student |
| `hidden_tests` | list[TestCase] | Used for scoring; inputs never returned to client |
| `expected_output_format` | string | Short note on return type / encoding |

## TestCase

```json
{
  "id": "v1",
  "description": "Target in the middle",
  "args": [[1, 3, 5, 7, 9], 5],
  "kwargs": {},
  "expected": 2,
  "is_edge_case": false,
  "performance_weight": 0
}
```

| Field | Description |
|-------|-------------|
| `id` | Unique within the problem |
| `description` | Shown for visible tests only |
| `args` / `kwargs` | Passed to the student function |
| `expected` | Deep-equality target (JSON-compatible) |
| `is_edge_case` | Counts toward edge-case score when true |
| `performance_weight` | Relative weight for performance score (0 = ignore) |

## Supported starter problems

- `binary-search`
- `merge-sort`
- `two-sum`
- `bfs`
- `dijkstra`

## Harness contract

The runner writes a small harness that:

1. Imports the student module as `solution`
2. Calls `getattr(solution, function_name)(*args, **kwargs)`
3. Compares the return value to `expected` with deep equality
4. Emits a JSON line result per test to stdout (controlled channel)

Students should implement only the required function and avoid reading stdin unless the problem asks for it.

## Adding a problem

1. Create `backend/codetrace/problems/data/<id>.json`
2. Register it in `problems/registry.py`
3. Add fixture solutions under `backend/tests/fixtures/`
4. Document it in the README
