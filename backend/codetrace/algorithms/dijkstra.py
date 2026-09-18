from __future__ import annotations

import heapq
from typing import Any

from codetrace.events.models import AlgorithmResult


def dijkstra(
    graph: dict[str, list[tuple[str, float]]],
    start: str,
) -> AlgorithmResult:
    """Dijkstra shortest paths. Edges are (neighbor, weight)."""
    events: list[dict] = []
    visited_count = relaxations = 0
    dist: dict[str, float] = {node: float("inf") for node in graph}
    prev: dict[str, str | None] = {node: None for node in graph}
    if start not in graph:
        metrics = {
            "comparisons": 0,
            "swaps": 0,
            "writes": 0,
            "visited": 0,
            "relaxations": 0,
        }
        result = {"distances": {}, "previous": {}}
        events.append({"type": "complete", "result": result, "metrics": metrics})
        return AlgorithmResult(
            algorithm="dijkstra",
            input={"graph": _serialize_graph(graph), "start": start},
            events=events,
            result=result,
            metrics=metrics,
        )

    dist[start] = 0.0
    heap: list[tuple[float, str]] = [(0.0, start)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        visited_count += 1
        events.append({"type": "visit", "node": node, "structure": "graph", "distance": d})
        for neighbor, weight in graph.get(node, []):
            if neighbor not in dist:
                dist[neighbor] = float("inf")
                prev[neighbor] = None
            old = dist[neighbor]
            new = d + weight
            if new < old:
                relaxations += 1
                dist[neighbor] = new
                prev[neighbor] = node
                heapq.heappush(heap, (new, neighbor))
                events.append(
                    {
                        "type": "relax_edge",
                        "from": node,
                        "to": neighbor,
                        "weight": weight,
                        "old_distance": None if old == float("inf") else old,
                        "new_distance": new,
                    }
                )

    distances = {k: (None if v == float("inf") else v) for k, v in dist.items()}
    result = {"distances": distances, "previous": prev}
    metrics = {
        "comparisons": 0,
        "swaps": 0,
        "writes": 0,
        "visited": visited_count,
        "relaxations": relaxations,
    }
    events.append({"type": "complete", "result": result, "metrics": metrics})
    return AlgorithmResult(
        algorithm="dijkstra",
        input={"graph": _serialize_graph(graph), "start": start},
        events=events,
        result=result,
        metrics=metrics,
    )


def _serialize_graph(graph: dict[str, list[tuple[str, float]]]) -> dict[str, list[list[Any]]]:
    return {k: [[n, w] for n, w in edges] for k, edges in graph.items()}


def parse_weighted_graph(raw: dict[str, list]) -> dict[str, list[tuple[str, float]]]:
    parsed: dict[str, list[tuple[str, float]]] = {}
    for node, edges in raw.items():
        parsed[str(node)] = []
        for edge in edges:
            if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                parsed[str(node)].append((str(edge[0]), float(edge[1])))
            else:
                # unweighted fallback
                parsed[str(node)].append((str(edge), 1.0))
    return parsed
