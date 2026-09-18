import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api/client";
import type { AlgorithmMeta } from "../types";

type Point = {
  input_size: number;
  a: Record<string, unknown>;
  b: Record<string, unknown>;
};

export function ComparePage() {
  const [algos, setAlgos] = useState<AlgorithmMeta[]>([]);
  const [a, setA] = useState("bubble-sort");
  const [b, setB] = useState("insertion-sort");
  const [points, setPoints] = useState<Point[]>([]);
  const [disclaimer, setDisclaimer] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.algorithms().then((list) => {
      setAlgos(list.filter((x) => x.category === "sorting"));
    });
  }, []);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.compare([a, b], [10, 25, 50, 75, 100]);
      setPoints(res.points);
      setDisclaimer(res.disclaimer);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  const chartData = useMemo(
    () =>
      points.map((p) => ({
        size: p.input_size,
        [`${a} time`]: p.a.execution_time_ms,
        [`${b} time`]: p.b.execution_time_ms,
        [`${a} comparisons`]: p.a.comparisons,
        [`${b} comparisons`]: p.b.comparisons,
      })),
    [points, a, b],
  );

  const latest = points[points.length - 1];

  return (
    <div>
      <h1 className="font-display text-4xl mb-2">Algorithm comparison</h1>
      <p className="text-slate mb-6 max-w-2xl">
        Compare two sorting algorithms on growing input sizes. Timing reflects this
        environment and is not a formal benchmark.
      </p>

      <div className="flex flex-wrap gap-4 mb-4">
        <label className="text-sm">
          Algorithm A
          <select className="field mt-1 block" value={a} onChange={(e) => setA(e.target.value)}>
            {algos.map((x) => (
              <option key={x.id} value={x.id}>
                {x.title}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Algorithm B
          <select className="field mt-1 block" value={b} onChange={(e) => setB(e.target.value)}>
            {algos.map((x) => (
              <option key={x.id} value={x.id}>
                {x.title}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="btn-primary self-end" disabled={loading} onClick={run}>
          {loading ? "Running…" : "Compare"}
        </button>
      </div>

      {error && <p className="text-accent">{error}</p>}
      {disclaimer && <p className="text-sm text-slate mb-4 italic">{disclaimer}</p>}

      {latest && (
        <div className="overflow-x-auto mb-8">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="border-b border-ink/20">
                <th className="py-2">Metric</th>
                <th>{String(latest.a.title)}</th>
                <th>{String(latest.b.title)}</th>
              </tr>
            </thead>
            <tbody>
              {(
                [
                  ["Input size", latest.input_size, latest.input_size],
                  ["Execution time (ms)", latest.a.execution_time_ms, latest.b.execution_time_ms],
                  ["Comparisons", latest.a.comparisons, latest.b.comparisons],
                  ["Swaps", latest.a.swaps, latest.b.swaps],
                  ["Writes", latest.a.writes, latest.b.writes],
                  ["Memory estimate", latest.a.memory_estimate, latest.b.memory_estimate],
                  ["Completed", String(latest.a.completed), String(latest.b.completed)],
                  ["Time complexity", latest.a.time_complexity, latest.b.time_complexity],
                  ["Space complexity", latest.a.space_complexity, latest.b.space_complexity],
                ] as Array<[string, unknown, unknown]>
              ).map(([label, va, vb]) => (
                <tr key={label} className="border-b border-ink/10">
                  <td className="py-2 text-slate">{label}</td>
                  <td className="font-mono">{String(va)}</td>
                  <td className="font-mono">{String(vb)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {chartData.length > 0 && (
        <div className="h-80 w-full">
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d6d3c9" />
              <XAxis dataKey="size" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey={`${a} comparisons`} stroke="#0d9488" strokeWidth={2} />
              <Line type="monotone" dataKey={`${b} comparisons`} stroke="#0369a1" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
