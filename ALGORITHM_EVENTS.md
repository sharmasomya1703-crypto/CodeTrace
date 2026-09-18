# Algorithm Event Format

CodeTrace algorithms do not mutate React state directly. Each algorithm returns a sequence of structured events that the visualizer replays.

## Envelope

```json
{
  "algorithm": "bubble-sort",
  "input": [5, 3, 1, 4],
  "events": [ ... ],
  "result": [1, 3, 4, 5],
  "metrics": {
    "comparisons": 6,
    "swaps": 4,
    "writes": 0,
    "visited": 0
  }
}
```

## Event types

Every event has a `type` string. Optional fields depend on the type.

### `compare`

Two elements (or nodes) are compared.

```json
{ "type": "compare", "indices": [1, 2], "values": [4, 3] }
```

For graphs, use node ids:

```json
{ "type": "compare", "nodes": ["A", "B"], "values": [1, 2] }
```

### `swap`

Two array indices exchange values.

```json
{ "type": "swap", "indices": [1, 2], "values": [4, 3] }
```

### `overwrite`

An index is written with a new value (merge / insertion style).

```json
{ "type": "overwrite", "index": 2, "value": 3, "previous": 5 }
```

### `visit`

A node or index is visited during search / traversal.

```json
{ "type": "visit", "node": "B", "structure": "graph" }
```

```json
{ "type": "visit", "index": 3, "value": 7, "structure": "array" }
```

### `enqueue` / `dequeue`

Queue operations for BFS (and similar).

```json
{ "type": "enqueue", "node": "C", "queue": ["B", "C"] }
```

```json
{ "type": "dequeue", "node": "B", "queue": ["C"] }
```

### `push` / `pop`

Stack operations for DFS.

```json
{ "type": "push", "node": "C", "stack": ["A", "C"] }
```

```json
{ "type": "pop", "node": "C", "stack": ["A"] }
```

### `relax_edge`

Dijkstra (or Bellman-Ford style) distance update.

```json
{
  "type": "relax_edge",
  "from": "A",
  "to": "B",
  "weight": 4,
  "old_distance": null,
  "new_distance": 4
}
```

### `highlight`

Optional UI hint (sorted region, pivot, etc.).

```json
{ "type": "highlight", "indices": [0, 1, 2], "role": "sorted" }
```

```json
{ "type": "highlight", "index": 3, "role": "pivot" }
```

### `set_key` / `found` / `not_found`

Search outcomes.

```json
{ "type": "found", "index": 2, "value": 5 }
```

```json
{ "type": "not_found", "target": 9 }
```

### `complete`

Terminal event. Always last.

```json
{
  "type": "complete",
  "result": [1, 3, 4, 5],
  "metrics": { "comparisons": 6, "swaps": 4 }
}
```

## Rules

1. Events must be JSON-serializable plain objects.
2. Replaying events in order must reproduce the final `result` state for array algorithms.
3. Metrics counted during generation must match the number of corresponding events (where applicable).
4. Algorithms never import React or UI modules.
5. Unknown event types should be ignored by renderers (forward compatible).

## Replay contract (arrays)

Starting from a copy of the input array:

| Event | Effect |
|-------|--------|
| `swap` | Swap `indices[0]` and `indices[1]` |
| `overwrite` | Set `array[index] = value` |
| `complete` | No mutation; asserts equality with `result` when testing |

`compare`, `visit`, `highlight` do not mutate array state.

## Graph state

Graph visualizers track visited sets, frontier (queue/stack), and distance maps from `visit`, `enqueue`/`dequeue`, `push`/`pop`, and `relax_edge` events.
