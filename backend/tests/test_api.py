from __future__ import annotations

from fastapi.testclient import TestClient

from codetrace.main import app

client = TestClient(app)


def test_health() -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"


def test_list_algorithms() -> None:
    res = client.get("/api/algorithms")
    assert res.status_code == 200
    ids = {a["id"] for a in res.json()}
    assert "bubble-sort" in ids
    assert "dijkstra" in ids


def test_visualize_bubble() -> None:
    res = client.post(
        "/api/visualize",
        json={"algorithm": "bubble-sort", "data": {"array": [3, 1, 2]}},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["result"] == [1, 2, 3]
    assert body["events"][-1]["type"] == "complete"


def test_problems_hide_hidden_inputs() -> None:
    res = client.get("/api/problems/binary-search")
    assert res.status_code == 200
    body = res.json()
    assert "hidden_tests" not in body
    assert body["hidden_test_count"] >= 1


def test_evaluate_endpoint() -> None:
    source = """
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
"""
    res = client.post(
        "/api/evaluate",
        json={"problem_id": "binary-search", "source": source},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["scores"]["overall"] == 100.0
    assert "hidden_tests" not in body
