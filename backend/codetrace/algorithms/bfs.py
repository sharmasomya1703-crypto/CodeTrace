from __future__ import annotations

from collections import deque
from typing import Any

from codetrace.events.models import AlgorithmResult


def breadth_first_search(
    graph: dict[str, list[str]],
    start: str,
) -> AlgorithmResult:
    """Unweighted BFS. Graph is adjacency list of node -> neighbors."""
    events: list[dict] = []
    visited_count = enqueues = 0
    order: list[str] = []
    visited: set[str] = set()
    queue: deque[str] = deque()

    if start not in graph:
        metrics = {"comparisons": 0, "swaps": 0, "writes": 0, "visited": 0, "enqueues": 0}
        events.append({"type": "complete", "result": order, "metrics": metrics})
        return AlgorithmResult(
            algorithm="bfs",
            input={"graph": graph, "start": start},
            events=events,
            result=order,
            metrics=metrics,
        )

    queue.append(start)
    enqueues += 1
    events.append({"type": "enqueue", "node": start, "queue": list(queue)})
    visited.add(start)

    while queue:
        node = queue.popleft()
        events.append({"type": "dequeue", "node": node, "queue": list(queue)})
        visited_count += 1
        events.append({"type": "visit", "node": node, "structure": "graph"})
        order.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                enqueues += 1
                events.append({"type": "enqueue", "node": neighbor, "queue": list(queue)})

    metrics = {
        "comparisons": 0,
        "swaps": 0,
        "writes": 0,
        "visited": visited_count,
        "enqueues": enqueues,
    }
    events.append({"type": "complete", "result": order, "metrics": metrics})
    return AlgorithmResult(
        algorithm="bfs",
        input={"graph": graph, "start": start},
        events=events,
        result=order,
        metrics=metrics,
    )


def normalize_graph(raw: dict[str, Any]) -> dict[str, list[str]]:
    return {str(k): [str(n) for n in v] for k, v in raw.items()}
