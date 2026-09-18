from __future__ import annotations

import json

from codetrace.cli import main


def test_cli_list(capsys) -> None:
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "bubble-sort" in out
    assert "binary-search" in out


def test_cli_show(capsys) -> None:
    assert main(["show", "binary-search"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["id"] == "binary-search"
    assert "hidden_tests" not in data


def test_cli_evaluate_json(tmp_path, capsys) -> None:
    sol = tmp_path / "solution.py"
    sol.write_text(
        """
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
""",
        encoding="utf-8",
    )
    code = main(["evaluate", str(sol), "--problem", "binary-search", "--format", "json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["scores"]["overall"] == 100.0
