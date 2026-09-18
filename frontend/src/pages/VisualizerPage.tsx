import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { PlaybackControls } from "../components/PlaybackControls";
import { usePlayback } from "../hooks/usePlayback";
import type { AlgorithmMeta, AlgorithmResult } from "../types";
import { ArrayVisualizer } from "../visualizers/ArrayVisualizer";
import { GraphVisualizer } from "../visualizers/GraphVisualizer";

function generateInWorker(
  size: number,
  mode: "random" | "sorted" | "reverse",
  seed: number,
): Promise<number[]> {
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL("../workers/arrayWorker.ts", import.meta.url), {
      type: "module",
    });
    worker.onmessage = (ev: MessageEvent<{ array: number[] }>) => {
      resolve(ev.data.array);
      worker.terminate();
    };
    worker.onerror = (err) => {
      reject(err);
      worker.terminate();
    };
    worker.postMessage({ type: "generate", size, mode, seed });
  });
}

const DEFAULT_GRAPH: Record<string, string[]> = {
  A: ["B", "C"],
  B: ["D"],
  C: ["D", "E"],
  D: ["F"],
  E: ["F"],
  F: [],
};

const DEFAULT_WEIGHTED: Record<string, [string, number][]> = {
  A: [
    ["B", 1],
    ["C", 4],
  ],
  B: [
    ["C", 2],
    ["D", 5],
  ],
  C: [["D", 1]],
  D: [],
};

export function VisualizerPage() {
  const [params] = useSearchParams();
  const [algos, setAlgos] = useState<AlgorithmMeta[]>([]);
  const [algoId, setAlgoId] = useState(params.get("algo") ?? "bubble-sort");
  const [arrayText, setArrayText] = useState("5, 3, 8, 1, 4, 7, 2");
  const [target, setTarget] = useState(4);
  const [size, setSize] = useState(12);
  const [result, setResult] = useState<AlgorithmResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const meta = algos.find((a) => a.id === algoId);
  const playback = usePlayback(result?.events ?? []);

  useEffect(() => {
    api.algorithms().then(setAlgos).catch((e: Error) => setError(e.message));
  }, []);

  const initialArray = useMemo(
    () =>
      arrayText
        .split(/[,\s]+/)
        .filter(Boolean)
        .map((x) => Number(x))
        .filter((n) => !Number.isNaN(n)),
    [arrayText],
  );

  async function load(mode?: "random" | "sorted" | "reverse") {
    setLoading(true);
    setError(null);
    try {
      let data: Record<string, unknown> = {};
      const category = algos.find((a) => a.id === algoId)?.category ?? "sorting";
      if (category === "graph") {
        if (algoId === "dijkstra") {
          data = { graph: DEFAULT_WEIGHTED, start: "A" };
        } else {
          data = { graph: DEFAULT_GRAPH, start: "A" };
        }
      } else {
        let arr = initialArray;
        if (mode) {
          arr = await generateInWorker(size, mode, 42);
          setArrayText(arr.join(", "));
        }
        if (category === "searching") {
          const sorted = [...arr].sort((a, b) => a - b);
          if (algoId === "binary-search") {
            arr = sorted;
            setArrayText(arr.join(", "));
          }
          data = { array: arr, target };
        } else {
          data = { array: arr };
        }
      }
      const res = await api.visualize(algoId, data);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (algos.length) void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [algoId, algos.length]);

  const opLabel = playback.current
    ? `${playback.current.type}${
        playback.current.indices ? ` [${playback.current.indices.join(", ")}]` : ""
      }${playback.current.node ? ` ${playback.current.node}` : ""}`
    : "—";

  return (
    <div>
      <h1 className="font-display text-4xl mb-2">Visualizer</h1>
      <p className="text-slate mb-6">
        Algorithms emit structured events; this page only replays them.
      </p>

      <div className="flex flex-wrap gap-4 mb-6">
        <label className="text-sm">
          Algorithm
          <select
            className="field mt-1 block"
            value={algoId}
            onChange={(e) => setAlgoId(e.target.value)}
          >
            {algos.map((a) => (
              <option key={a.id} value={a.id}>
                {a.title}
              </option>
            ))}
          </select>
        </label>
        {meta?.category !== "graph" && (
          <>
            <label className="text-sm flex-1 min-w-[12rem]">
              Array
              <input
                className="field mt-1 block w-full"
                value={arrayText}
                onChange={(e) => setArrayText(e.target.value)}
              />
            </label>
            {meta?.category === "searching" && (
              <label className="text-sm">
                Target
                <input
                  type="number"
                  className="field mt-1 block w-24"
                  value={target}
                  onChange={(e) => setTarget(Number(e.target.value))}
                />
              </label>
            )}
            <label className="text-sm">
              Size
              <input
                type="number"
                className="field mt-1 block w-20"
                value={size}
                min={0}
                max={40}
                onChange={(e) => setSize(Number(e.target.value))}
              />
            </label>
          </>
        )}
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        <button type="button" className="btn-primary" disabled={loading} onClick={() => load()}>
          {loading ? "Loading…" : "Run"}
        </button>
        {meta?.category !== "graph" && (
          <>
            <button type="button" className="btn-secondary" onClick={() => load("random")}>
              Random
            </button>
            <button type="button" className="btn-secondary" onClick={() => load("sorted")}>
              Sorted
            </button>
            <button type="button" className="btn-secondary" onClick={() => load("reverse")}>
              Reverse
            </button>
          </>
        )}
      </div>

      {error && <p className="text-accent mb-4">{error}</p>}

      {result && (
        <>
          <PlaybackControls
            playing={playback.playing}
            speed={playback.speed}
            onPlay={playback.play}
            onPause={playback.pause}
            onStep={playback.stepForward}
            onReset={playback.reset}
            onSpeed={playback.setSpeed}
          />

          <div className="mt-6 grid md:grid-cols-[1fr_14rem] gap-6">
            <div className="bg-paper/60 border border-ink/10 p-4">
              {meta?.category === "graph" ? (
                <GraphVisualizer
                  graph={
                    (result.input as { graph: Record<string, unknown> }).graph ??
                    (algoId === "dijkstra" ? DEFAULT_WEIGHTED : DEFAULT_GRAPH)
                  }
                  events={result.events}
                  index={playback.index}
                  current={playback.current}
                  weighted={algoId === "dijkstra"}
                />
              ) : (
                <ArrayVisualizer
                  initial={
                    Array.isArray(result.input)
                      ? (result.input as number[])
                      : ((result.input as { array: number[] }).array ?? [])
                  }
                  events={result.events}
                  index={playback.index}
                  current={playback.current}
                />
              )}
            </div>
            <aside className="text-sm space-y-3">
              <div>
                <p className="text-slate">Current operation</p>
                <p className="font-mono">{opLabel}</p>
              </div>
              <div>
                <p className="text-slate">Step</p>
                <p className="font-mono">
                  {playback.index + 1} / {result.events.length}
                </p>
              </div>
              <div>
                <p className="text-slate">Metrics</p>
                <ul className="font-mono text-xs space-y-1">
                  {Object.entries(result.metrics).map(([k, v]) => (
                    <li key={k}>
                      {k}: {v}
                    </li>
                  ))}
                </ul>
              </div>
            </aside>
          </div>
        </>
      )}
    </div>
  );
}
