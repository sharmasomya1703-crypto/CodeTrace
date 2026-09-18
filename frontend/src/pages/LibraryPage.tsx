import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { AlgorithmMeta } from "../types";

export function LibraryPage() {
  const [items, setItems] = useState<AlgorithmMeta[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .algorithms()
      .then(setItems)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <p className="text-accent">Failed to load: {error}</p>;

  const groups = ["sorting", "searching", "graph"] as const;

  return (
    <div>
      <h1 className="font-display text-4xl mb-2">Algorithm library</h1>
      <p className="text-slate mb-8">Explanations, complexity, and links to the visualizer.</p>
      {groups.map((cat) => (
        <section key={cat} className="mb-10">
          <h2 className="font-display text-2xl capitalize mb-4">{cat}</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {items
              .filter((a) => a.category === cat)
              .map((a) => (
                <article key={a.id} className="border-t border-ink/15 pt-4">
                  <div className="flex items-baseline justify-between gap-3">
                    <h3 className="font-display text-xl">{a.title}</h3>
                    <Link className="text-sea text-sm hover:underline" to={`/visualize?algo=${a.id}`}>
                      Visualize
                    </Link>
                  </div>
                  <p className="text-slate mt-2">{a.description}</p>
                  <p className="font-mono text-xs mt-3 text-ink/70">
                    Time {a.time_complexity} · Space {a.space_complexity}
                    {a.stable != null && ` · ${a.stable ? "stable" : "unstable"}`}
                    {a.in_place != null && ` · ${a.in_place ? "in-place" : "not in-place"}`}
                  </p>
                  <details className="mt-3">
                    <summary className="cursor-pointer text-sm text-ink">Details</summary>
                    <pre className="mt-2 text-xs font-mono bg-ink/5 p-3 overflow-x-auto whitespace-pre-wrap">
                      {a.pseudocode}
                    </pre>
                    <p className="text-sm mt-2">
                      <strong>Use cases:</strong> {a.use_cases.join("; ")}
                    </p>
                    <p className="text-sm mt-1">
                      <strong>Common mistakes:</strong> {a.common_mistakes.join("; ")}
                    </p>
                  </details>
                </article>
              ))}
          </div>
        </section>
      ))}
    </div>
  );
}
