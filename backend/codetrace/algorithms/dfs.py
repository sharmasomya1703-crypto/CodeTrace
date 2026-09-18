from __future__ import annotations

from typing import Any

from codetrace.events.models import AlgorithmResult


def depth_first_search(
    graph: dict[str, list[str]],
    start: str,
) -> AlgorithmResult:
    """Iterative DFS using an explicit stack."""
    events: list[dict] = []
    visited_count = 0
    order: list[str] = []
    visited: set[str] = set()
    stack: list[str] = []

    if start not in graph:
        metrics = {"comparisons": 0, "swaps": 0, "writes": 0, "visited": 0}
        events.append({"type": "complete", "result": order, "metrics": metrics})
        return AlgorithmResult(
            algorithm="dfs",
            input={"graph": graph, "start": start},
            events=events,
            result=order,
            metrics=metrics,
        )

    stack.append(start)
    events.append({"type": "push", "node": start, "stack": list(stack)})

    while stack:
        node = stack.pop()
        events.append({"type": "pop", "node": node, "stack": list(stack)})
        if node in visited:
            continue
        visited.add(node)
        visited_count += 1
        events.append({"type": "visit", "node": node, "structure": "graph"})
        order.append(node)
        # Push neighbors in reverse so first neighbor is processed first
        neighbors = list(graph.get(node, []))
        for neighbor in reversed(neighbors):
            if neighbor not in visited:
                stack.append(neighbor)
                events.append({"type": "push", "node": neighbor, "stack": list(stack)})

    metrics = {
        "comparisons": 0,
        "swaps": 0,
        "writes": 0,
        "visited": visited_count,
    }
    events.append({"type": "complete", "result": order, "metrics": metrics})
    return AlgorithmResult(
        algorithm="dfs",
        input={"graph": graph, "start": start},
        events=events,
        result=order,
        metrics=metrics,
    )


def normalize_graph(raw: dict[str, Any]) -> dict[str, list[str]]:
    return {str(k): [str(n) for n in v] for k, v in raw.items()}
