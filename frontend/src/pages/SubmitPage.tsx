import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { ProblemSummary } from "../types";

const STARTERS: Record<string, string> = {
  "binary-search": `def binary_search(arr: list[int], target: int) -> int:
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
`,
  "merge-sort": `def merge_sort(arr: list[int]) -> list[int]:
    return sorted(arr)
`,
  "two-sum": `def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, n in enumerate(nums):
        need = target - n
        if need in seen:
            a, b = seen[need], i
            return [a, b] if a < b else [b, a]
        seen[n] = i
    return []
`,
  bfs: `from collections import deque

def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
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
`,
  dijkstra: `import heapq

def dijkstra(graph: dict[str, list[list]], start: str) -> dict[str, float]:
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue
        for edge in graph.get(u, []):
            v, w = edge[0], edge[1]
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
`,
};

export function SubmitPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const [problem, setProblem] = useState<ProblemSummary | null>(null);
  const [source, setSource] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .problem(id)
      .then((p) => {
        setProblem(p);
        setSource(STARTERS[p.id] ?? `def ${p.function_name}(...):\n    pass\n`);
      })
      .catch((e: Error) => setError(e.message));
  }, [id]);

  async function onSubmit() {
    setSubmitting(true);
    setError(null);
    try {
      const result = await api.evaluate(id, source);
      navigate(`/evaluate/${id}`, { state: { result, source } });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSubmitting(false);
    }
  }

  function onFile(file: File | null) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setSource(String(reader.result ?? ""));
    reader.readAsText(file);
  }

  if (error && !problem) return <p className="text-accent">{error}</p>;
  if (!problem) return <p className="text-slate">Loading…</p>;

  return (
    <div>
      <p className="text-sm text-slate mb-2">
        <Link to={`/problems/${id}`} className="hover:underline">
          {problem.title}
        </Link>{" "}
        / submit
      </p>
      <h1 className="font-display text-4xl mb-2">Submit solution</h1>
      <p className="font-mono text-sm mb-4">{problem.signature}</p>

      <label className="btn-secondary cursor-pointer inline-block mb-3">
        Upload .py
        <input
          type="file"
          accept=".py,text/x-python,text/plain"
          className="hidden"
          onChange={(e) => onFile(e.target.files?.[0] ?? null)}
        />
      </label>
      <textarea
        className="field w-full min-h-[240px] font-mono text-sm"
        value={source}
        onChange={(e) => setSource(e.target.value)}
        spellCheck={false}
      />
      {error && <p className="text-accent mt-2">{error}</p>}
      <button type="button" className="btn-primary mt-4" disabled={submitting} onClick={onSubmit}>
        {submitting ? "Evaluating…" : "Evaluate"}
      </button>
      <p className="text-xs text-slate mt-3 max-w-xl">
        Executed via subprocess isolation outside the API process. Not a complete security sandbox.
      </p>
    </div>
  );
}
