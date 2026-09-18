from __future__ import annotations

import random
import time
from typing import Any

from codetrace.algorithms.registry import (
    get_algorithm,
    list_algorithms,
    meta_to_dict,
    run_algorithm,
)
from codetrace.events.models import AlgorithmResult


def generate_array(
    size: int,
    mode: str = "random",
    seed: int | None = None,
    low: int = 0,
    high: int = 99,
) -> list[int]:
    rng = random.Random(seed)
    if size < 0:
        raise ValueError("size must be >= 0")
    if mode == "sorted":
        return list(range(size))
    if mode == "reverse":
        return list(range(size - 1, -1, -1))
    return [rng.randint(low, high) for _ in range(size)]


def visualize(algorithm_id: str, data: dict[str, Any]) -> AlgorithmResult:
    return run_algorithm(algorithm_id, data)


def algorithm_catalog() -> list[dict[str, Any]]:
    return [meta_to_dict(m) for m in list_algorithms()]


def compare_pair(
    algo_a: str,
    algo_b: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Run two algorithms on the same input and collect metrics + wall time."""
    start_a = time.perf_counter()
    result_a = run_algorithm(algo_a, data)
    time_a = (time.perf_counter() - start_a) * 1000

    start_b = time.perf_counter()
    result_b = run_algorithm(algo_b, data)
    time_b = (time.perf_counter() - start_b) * 1000

    meta_a = get_algorithm(algo_a)
    meta_b = get_algorithm(algo_b)

    def pack(meta, result: AlgorithmResult, ms: float) -> dict[str, Any]:
        return {
            "id": meta.id,
            "title": meta.title,
            "execution_time_ms": round(ms, 4),
            "comparisons": result.metrics.get("comparisons", 0),
            "swaps": result.metrics.get("swaps", 0),
            "writes": result.metrics.get("writes", 0),
            "visited": result.metrics.get("visited", 0),
            "memory_estimate": _memory_estimate(meta, data),
            "completed": result.events[-1]["type"] == "complete" if result.events else False,
            "time_complexity": meta.time_complexity,
            "space_complexity": meta.space_complexity,
            "result": result.result,
        }

    input_size = _input_size(data)
    return {
        "input_size": input_size,
        "disclaimer": (
            "Browser/server timing is affected by the environment and is not a formal benchmark."
        ),
        "a": pack(meta_a, result_a, time_a),
        "b": pack(meta_b, result_b, time_b),
    }


def compare_scaling(
    algo_a: str,
    algo_b: str,
    sizes: list[int],
    mode: str = "random",
    seed: int = 42,
    category_hint: str | None = None,
) -> dict[str, Any]:
    points = []
    meta_a = get_algorithm(algo_a)
    category = category_hint or meta_a.category
    for size in sizes:
        if category == "sorting":
            data = {"array": generate_array(size, mode=mode, seed=seed + size)}
        elif category == "searching":
            arr = generate_array(size, mode="sorted", seed=seed + size)
            target = arr[size // 2] if arr else 0
            data = {"array": arr, "target": target}
        else:
            # simple line graph for scaling demos
            graph = {str(i): [str(i + 1)] if i + 1 < size else [] for i in range(max(size, 1))}
            data = {"graph": graph, "start": "0"}
        points.append(compare_pair(algo_a, algo_b, data))
    return {
        "sizes": sizes,
        "points": points,
        "disclaimer": (
            "Browser/server timing is affected by the environment and is not a formal benchmark."
        ),
    }


def _input_size(data: dict[str, Any]) -> int:
    if "array" in data:
        return len(data["array"])
    if "graph" in data:
        return len(data["graph"])
    return 0


def _memory_estimate(meta, data: dict[str, Any]) -> str:
    n = _input_size(data)
    if meta.space_complexity.startswith("O(1)"):
        return f"~O(1) auxiliary (n={n})"
    if "log" in meta.space_complexity:
        return f"~O(log n) auxiliary (n={n})"
    return f"~O(n) auxiliary (n={n})"
