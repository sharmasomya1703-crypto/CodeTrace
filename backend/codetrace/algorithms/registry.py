from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from codetrace.algorithms.bfs import breadth_first_search
from codetrace.algorithms.binary_search import binary_search
from codetrace.algorithms.bubble_sort import bubble_sort
from codetrace.algorithms.dfs import depth_first_search
from codetrace.algorithms.dijkstra import dijkstra, parse_weighted_graph
from codetrace.algorithms.insertion_sort import insertion_sort
from codetrace.algorithms.linear_search import linear_search
from codetrace.algorithms.merge_sort import merge_sort
from codetrace.algorithms.quick_sort import quick_sort
from codetrace.events.models import AlgorithmResult


@dataclass(frozen=True)
class AlgorithmMeta:
    id: str
    title: str
    category: str  # sorting | searching | graph
    description: str
    pseudocode: str
    time_complexity: str
    space_complexity: str
    stable: bool | None
    in_place: bool | None
    use_cases: list[str]
    common_mistakes: list[str]
    runner: Callable[..., AlgorithmResult]


def _meta(**kwargs: Any) -> AlgorithmMeta:
    return AlgorithmMeta(**kwargs)


ALGORITHMS: dict[str, AlgorithmMeta] = {
    "bubble-sort": _meta(
        id="bubble-sort",
        title="Bubble Sort",
        category="sorting",
        description="Repeatedly compares adjacent elements and swaps them if they are out of order.",
        pseudocode="""for i in 0..n-1:
  for j in 0..n-i-2:
    if a[j] > a[j+1]:
      swap(a[j], a[j+1])""",
        time_complexity="O(n²)",
        space_complexity="O(1)",
        stable=True,
        in_place=True,
        use_cases=["Teaching comparisons/swaps", "Tiny nearly-sorted arrays"],
        common_mistakes=["Forgetting the early-exit flag", "Off-by-one on inner loop"],
        runner=lambda data: bubble_sort(data["array"]),
    ),
    "insertion-sort": _meta(
        id="insertion-sort",
        title="Insertion Sort",
        category="sorting",
        description="Builds a sorted prefix by inserting each next element into its place.",
        pseudocode="""for i in 1..n-1:
  key = a[i]
  shift larger elements right
  place key""",
        time_complexity="O(n²) worst, O(n) best",
        space_complexity="O(1)",
        stable=True,
        in_place=True,
        use_cases=["Small arrays", "Nearly sorted data", "Online insertion"],
        common_mistakes=["Confusing write indices", "Unstable implementation with equals"],
        runner=lambda data: insertion_sort(data["array"]),
    ),
    "merge-sort": _meta(
        id="merge-sort",
        title="Merge Sort",
        category="sorting",
        description="Divide-and-conquer sort that merges two sorted halves.",
        pseudocode="""merge_sort(a):
  if len <= 1: return
  mid = n//2
  sort left, sort right
  merge halves""",
        time_complexity="O(n log n)",
        space_complexity="O(n)",
        stable=True,
        in_place=False,
        use_cases=["Stable sort needed", "Linked lists", "External sorting ideas"],
        common_mistakes=["Incorrect mid when merging", "Not copying leftover runs"],
        runner=lambda data: merge_sort(data["array"]),
    ),
    "quick-sort": _meta(
        id="quick-sort",
        title="Quick Sort",
        category="sorting",
        description="Partitions around a pivot, then recursively sorts partitions.",
        pseudocode="""quick_sort(low, high):
  if low < high:
    p = partition(low, high)
    quick_sort(low, p-1)
    quick_sort(p+1, high)""",
        time_complexity="O(n log n) avg, O(n²) worst",
        space_complexity="O(log n) avg",
        stable=False,
        in_place=True,
        use_cases=["General-purpose in-memory sorting", "When average speed matters"],
        common_mistakes=["Bad pivot on sorted input", "Forgetting to swap pivot into place"],
        runner=lambda data: quick_sort(data["array"]),
    ),
    "linear-search": _meta(
        id="linear-search",
        title="Linear Search",
        category="searching",
        description="Scans each element until the target is found.",
        pseudocode="""for i, x in enumerate(a):
  if x == target: return i
return -1""",
        time_complexity="O(n)",
        space_complexity="O(1)",
        stable=None,
        in_place=None,
        use_cases=["Unsorted data", "Small lists"],
        common_mistakes=["Assuming sorted input", "Off-by-one when not found"],
        runner=lambda data: linear_search(data["array"], data["target"]),
    ),
    "binary-search": _meta(
        id="binary-search",
        title="Binary Search",
        category="searching",
        description="Halves a sorted range each step until the target is found.",
        pseudocode="""low, high = 0, n-1
while low <= high:
  mid = (low+high)//2
  if a[mid] == target: return mid
  elif a[mid] < target: low = mid+1
  else: high = mid-1""",
        time_complexity="O(log n)",
        space_complexity="O(1)",
        stable=None,
        in_place=None,
        use_cases=["Sorted arrays", "Lower/upper bound queries"],
        common_mistakes=["Running on unsorted data", "Infinite loop with bad mid update"],
        runner=lambda data: binary_search(data["array"], data["target"]),
    ),
    "bfs": _meta(
        id="bfs",
        title="Breadth-First Search",
        category="graph",
        description="Explores neighbors level by level using a queue.",
        pseudocode="""queue = [start]
visited = {start}
while queue:
  u = dequeue()
  for v in neighbors(u):
    if v not visited: enqueue(v)""",
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        stable=None,
        in_place=None,
        use_cases=["Shortest path in unweighted graphs", "Level-order traversal"],
        common_mistakes=["Marking visited too late (duplicates)", "Forgetting disconnected nodes"],
        runner=lambda data: breadth_first_search(data["graph"], data["start"]),
    ),
    "dfs": _meta(
        id="dfs",
        title="Depth-First Search",
        category="graph",
        description="Explores as deep as possible along each branch using a stack.",
        pseudocode="""stack = [start]
while stack:
  u = pop()
  if u visited: continue
  visit u
  push unvisited neighbors""",
        time_complexity="O(V + E)",
        space_complexity="O(V)",
        stable=None,
        in_place=None,
        use_cases=["Cycle detection", "Topological ideas", "Connectivity"],
        common_mistakes=["Confusing recursion stack with visited set", "Wrong neighbor order"],
        runner=lambda data: depth_first_search(data["graph"], data["start"]),
    ),
    "dijkstra": _meta(
        id="dijkstra",
        title="Dijkstra Shortest Path",
        category="graph",
        description="Computes shortest paths from a source in graphs with non-negative weights.",
        pseudocode="""dist[start]=0
pq.push(start)
while pq:
  u = pop min dist
  for each edge u->v:
    relax if dist[u]+w < dist[v]""",
        time_complexity="O((V + E) log V) with binary heap",
        space_complexity="O(V)",
        stable=None,
        in_place=None,
        use_cases=["Road maps", "Routing with non-negative weights"],
        common_mistakes=["Using on negative weights", "Not skipping stale heap entries"],
        runner=lambda data: dijkstra(parse_weighted_graph(data["graph"]), data["start"]),
    ),
}


def list_algorithms() -> list[AlgorithmMeta]:
    return list(ALGORITHMS.values())


def get_algorithm(algorithm_id: str) -> AlgorithmMeta:
    if algorithm_id not in ALGORITHMS:
        raise KeyError(f"Unknown algorithm: {algorithm_id}")
    return ALGORITHMS[algorithm_id]


def run_algorithm(algorithm_id: str, data: dict[str, Any]) -> AlgorithmResult:
    meta = get_algorithm(algorithm_id)
    return meta.runner(data)


def meta_to_dict(meta: AlgorithmMeta) -> dict[str, Any]:
    return {
        "id": meta.id,
        "title": meta.title,
        "category": meta.category,
        "description": meta.description,
        "pseudocode": meta.pseudocode,
        "time_complexity": meta.time_complexity,
        "space_complexity": meta.space_complexity,
        "stable": meta.stable,
        "in_place": meta.in_place,
        "use_cases": meta.use_cases,
        "common_mistakes": meta.common_mistakes,
    }
