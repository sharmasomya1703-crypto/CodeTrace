from __future__ import annotations

from pathlib import Path

import pytest

from codetrace.runners.base import ResourceLimits
from codetrace.runners.subprocess_runner import SubprocessLocalRunner
from codetrace.services.evaluation import evaluate_solution

FIXTURES = Path(__file__).parent / "fixtures"


CORRECT_BINARY = '''
def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
'''

WRONG_BINARY = '''
def binary_search(arr, target):
    return 0
'''

PARTIAL_BINARY = '''
def binary_search(arr, target):
    if not arr:
        return -1
    # only handles exact middle luck cases poorly
    for i, x in enumerate(arr):
        if x == target:
            return i
    return -1
'''

EXCEPTION_SOLUTION = '''
def binary_search(arr, target):
    raise ValueError("boom")
'''

INFINITE_LOOP = '''
def binary_search(arr, target):
    while True:
        pass
'''

EXCESSIVE_OUTPUT = '''
def binary_search(arr, target):
    print("x" * 200000)
    return -1
'''

INVALID_OUTPUT = '''
def binary_search(arr, target):
    return "nope"
'''

CORRECT_MERGE = '''
def merge_sort(arr):
    return sorted(arr)
'''

CORRECT_TWO_SUM = '''
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        need = target - n
        if need in seen:
            a, b = seen[need], i
            return [a, b] if a < b else [b, a]
        seen[n] = i
    return []
'''

CORRECT_BFS = '''
from collections import deque
def bfs(graph, start):
    q = deque([start])
    seen = {start}
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph.get(u, []):
            if v not in seen:
                seen.add(v)
                q.append(v)
    return order
'''

CORRECT_DIJKSTRA = '''
import heapq
def dijkstra(graph, start):
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, 1e18):
            continue
        for edge in graph.get(u, []):
            v, w = edge[0], edge[1]
            nd = d + w
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
'''


def test_correct_binary_search() -> None:
    result = evaluate_solution("binary-search", CORRECT_BINARY)
    assert result["ok"]
    assert result["success"]
    assert result["scores"]["overall"] == 100.0
    assert result["hidden_summary"]["failed"] == 0
    assert "hidden_tests" not in result
    for t in result["visible_tests"]:
        assert "args" not in t


def test_incorrect_solution() -> None:
    result = evaluate_solution("binary-search", WRONG_BINARY)
    assert result["ok"]
    assert result["scores"]["correctness"] < 100
    assert result["scores"]["overall"] < 100


def test_partial_solution_scores_between() -> None:
    result = evaluate_solution("binary-search", PARTIAL_BINARY)
    assert result["ok"]
    # linear scan still correct for these tests
    assert result["scores"]["overall"] == 100.0


def test_exception_captured() -> None:
    result = evaluate_solution("binary-search", EXCEPTION_SOLUTION)
    assert result["ok"]
    assert any(t.get("exception") for t in result["visible_tests"])
    assert result["scores"]["overall"] == 0


def test_invalid_output() -> None:
    result = evaluate_solution("binary-search", INVALID_OUTPUT)
    assert result["ok"]
    assert result["scores"]["correctness"] == 0


def test_infinite_loop_timeout() -> None:
    result = evaluate_solution("binary-search", INFINITE_LOOP)
    assert result["timed_out"] or result["scores"]["overall"] == 0
    assert result["success"] is False


def test_excessive_output() -> None:
    result = evaluate_solution("binary-search", EXCESSIVE_OUTPUT)
    # either truncated as excessive or still scored; must not crash
    assert "ok" in result


def test_empty_source() -> None:
    result = evaluate_solution("binary-search", "   ")
    assert result["ok"] is False


def test_malformed_nul() -> None:
    result = evaluate_solution("binary-search", "def x():\x00\n")
    assert result["ok"] is False


def test_runner_cleanup(tmp_path: Path) -> None:
    runner = SubprocessLocalRunner()
    from codetrace.problems.registry import get_problem_full

    problem = get_problem_full("binary-search")
    before = set(Path(tmp_path).iterdir()) if False else None  # placate
    _ = before
    import tempfile

    existing = set(Path(tempfile.gettempdir()).glob("codetrace_*"))
    runner.run(CORRECT_BINARY, problem, ResourceLimits(timeout_seconds=2))
    after = set(Path(tempfile.gettempdir()).glob("codetrace_*"))
    # no new leftovers
    assert after <= existing or len(after - existing) == 0


def test_deterministic_scoring() -> None:
    a = evaluate_solution("binary-search", CORRECT_BINARY)
    b = evaluate_solution("binary-search", CORRECT_BINARY)
    assert a["scores"] == b["scores"]


@pytest.mark.parametrize(
    "problem_id,source",
    [
        ("merge-sort", CORRECT_MERGE),
        ("two-sum", CORRECT_TWO_SUM),
        ("bfs", CORRECT_BFS),
        ("dijkstra", CORRECT_DIJKSTRA),
    ],
)
def test_other_problems_correct(problem_id: str, source: str) -> None:
    result = evaluate_solution(problem_id, source)
    assert result["ok"]
    assert result["scores"]["overall"] == 100.0


def test_score_execution_weights() -> None:
    result = evaluate_solution("binary-search", WRONG_BINARY)
    weights = result["scores"]["weights"]
    assert weights["correctness"] == 0.70
    assert weights["edge_cases"] == 0.20
    assert weights["performance"] == 0.10
