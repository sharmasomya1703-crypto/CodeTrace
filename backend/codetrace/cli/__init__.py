from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from codetrace.algorithms.registry import list_algorithms
from codetrace.problems.registry import get_problem, list_problems
from codetrace.services.evaluation import evaluate_solution


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codetrace", description="CodeTrace CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List algorithms and problems")

    show_p = sub.add_parser("show", help="Show a problem definition")
    show_p.add_argument("problem_id")

    eval_p = sub.add_parser("evaluate", help="Evaluate a Python solution file")
    eval_p.add_argument("solution")
    eval_p.add_argument("--problem", required=True)
    eval_p.add_argument("--format", choices=["text", "json"], default="text")

    args = parser.parse_args(argv)

    if args.command == "list":
        print("Algorithms:")
        for meta in list_algorithms():
            print(f"  - {meta.id}: {meta.title} [{meta.category}]")
        print("\nProblems:")
        for problem in list_problems():
            print(f"  - {problem['id']}: {problem['title']}")
        return 0

    if args.command == "show":
        try:
            problem = get_problem(args.problem_id, include_hidden=False)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(json.dumps(problem, indent=2))
        return 0

    if args.command == "evaluate":
        path = Path(args.solution)
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            return 1
        try:
            source = path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"Malformed solution file: {exc}", file=sys.stderr)
            return 1
        result = evaluate_solution(args.problem, source)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            _print_eval_text(result)
        return 0 if result.get("ok") and result.get("success") else 1

    return 1


def _print_eval_text(result: dict) -> None:
    if not result.get("ok"):
        print(f"Error: {result.get('error')}")
        return
    scores = result["scores"]
    print(f"Problem: {result['problem_id']}")
    print(f"Overall: {scores['overall']}%")
    print(
        f"  Correctness: {scores['correctness']}%  "
        f"Edge cases: {scores['edge_cases']}%  "
        f"Performance: {scores['performance']}%"
    )
    print(f"Wall time: {result['wall_time_ms']} ms")
    if result.get("timed_out"):
        print("Timed out: yes")
    if result.get("error"):
        print(f"Runner note: {result['error']}")
    print("\nVisible tests:")
    for t in result["visible_tests"]:
        status = "PASS" if t["passed"] else "FAIL"
        print(f"  [{status}] {t['test_id']} ({t['runtime_ms']} ms)")
        if not t["passed"]:
            if t.get("exception"):
                print(f"    exception: {t['exception']}")
            print(f"    expected: {t.get('expected')}")
            print(f"    actual:   {t.get('actual')}")
    hidden = result["hidden_summary"]
    print(
        f"\nHidden tests: {hidden['passed']}/{hidden['total']} passed "
        "(inputs not shown)"
    )
    print(result.get("security_note", ""))


if __name__ == "__main__":
    raise SystemExit(main())
