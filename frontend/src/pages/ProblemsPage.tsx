import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { ProblemSummary } from "../types";

export function ProblemsPage() {
  const [items, setItems] = useState<ProblemSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .problems()
      .then(setItems)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) return <p className="text-accent">{error}</p>;

  return (
    <div>
      <h1 className="font-display text-4xl mb-2">Problems</h1>
      <p className="text-slate mb-8">
        Paste a Python solution and get scores from real test execution.
      </p>
      <ul className="space-y-6">
        {items.map((p) => (
          <li key={p.id} className="border-t border-ink/15 pt-4">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 className="font-display text-2xl">{p.title}</h2>
              <div className="flex gap-3 text-sm">
                <Link to={`/problems/${p.id}`} className="text-sea hover:underline">
                  Details
                </Link>
                <Link to={`/problems/${p.id}/submit`} className="text-accent hover:underline">
                  Submit
                </Link>
              </div>
            </div>
            <p className="text-slate mt-2 max-w-3xl">{p.description}</p>
            <p className="font-mono text-xs mt-2 text-ink/70">{p.signature}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
