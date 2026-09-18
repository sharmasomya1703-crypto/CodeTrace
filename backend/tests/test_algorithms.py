from __future__ import annotations

import pytest

from codetrace.algorithms.registry import ALGORITHMS, run_algorithm
from codetrace.events.models import validate_events
from codetrace.events.replay import replay_array_events

SORT_IDS = ["bubble-sort", "insertion-sort", "merge-sort", "quick-sort"]


@pytest.mark.parametrize("algo_id", SORT_IDS)
@pytest.mark.parametrize(
    "arr",
    [
        [],
        [1],
        [2, 1],
        [3, 1, 2],
        [5, 5, 5],
        [1, 2, 3, 4],
        [4, 3, 2, 1],
        [9, 1, 8, 2, 7, 3],
    ],
)
def test_sorting_correctness_and_replay(algo_id: str, arr: list[int]) -> None:
    result = run_algorithm(algo_id, {"array": arr})
    assert result.result == sorted(arr)
    errors = validate_events(result.events)
    assert errors == [], errors
    replayed = replay_array_events(arr, result.events)
    assert replayed == result.result


@pytest.mark.parametrize("algo_id", SORT_IDS)
def test_sorting_metrics_deterministic(algo_id: str) -> None:
    data = {"array": [5, 1, 4, 2, 8, 3]}
    a = run_algorithm(algo_id, data)
    b = run_algorithm(algo_id, data)
    assert a.metrics == b.metrics
    assert a.events == b.events


def test_linear_search() -> None:
    result = run_algorithm("linear-search", {"array": [4, 2, 9, 1], "target": 9})
    assert result.result == 2
    assert validate_events(result.events) == []
    miss = run_algorithm("linear-search", {"array": [1, 2, 3], "target": 9})
    assert miss.result == -1


def test_binary_search() -> None:
    arr = [1, 3, 5, 7, 9]
    hit = run_algorithm("binary-search", {"array": arr, "target": 7})
    assert hit.result == 3
    miss = run_algorithm("binary-search", {"array": arr, "target": 4})
    assert miss.result == -1
    empty = run_algorithm("binary-search", {"array": [], "target": 1})
    assert empty.result == -1


def test_bfs_order() -> None:
    graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    result = run_algorithm("bfs", {"graph": graph, "start": "A"})
    assert result.result == ["A", "B", "C", "D"]
    assert validate_events(result.events) == []


def test_dfs_visits_all() -> None:
    graph = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}
    result = run_algorithm("dfs", {"graph": graph, "start": "A"})
    assert set(result.result) == {"A", "B", "C", "D"}
    assert result.result[0] == "A"
    assert validate_events(result.events) == []


def test_dijkstra_distances() -> None:
    graph = {
        "A": [["B", 1], ["C", 4]],
        "B": [["C", 2], ["D", 5]],
        "C": [["D", 1]],
        "D": [],
    }
    result = run_algorithm("dijkstra", {"graph": graph, "start": "A"})
    distances = result.result["distances"]
    assert distances["A"] == 0
    assert distances["B"] == 1
    assert distances["C"] == 3
    assert distances["D"] == 4
    assert validate_events(result.events) == []


def test_all_algorithms_registered() -> None:
    expected = {
        "bubble-sort",
        "insertion-sort",
        "merge-sort",
        "quick-sort",
        "linear-search",
        "binary-search",
        "bfs",
        "dfs",
        "dijkstra",
    }
    assert set(ALGORITHMS) == expected
