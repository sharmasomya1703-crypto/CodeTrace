import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { ProblemSummary } from "../types";

export function ProblemDetailPage() {
  const { id = "" } = useParams();
  const [problem, setProblem] = useState<ProblemSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .problem(id)
      .then(setProblem)
      .catch((e: Error) => setError(e.message));
  }, [id]);

  if (error) return <p className="text-accent">{error}</p>;
  if (!problem) return <p className="text-slate">Loading…</p>;

  return (
    <div>
      <p className="text-sm text-slate mb-2">
        <Link to="/problems" className="hover:underline">
          Problems
        </Link>{" "}
        / {problem.id}
      </p>
      <h1 className="font-display text-4xl mb-2">{problem.title}</h1>
      <p className="text-slate max-w-3xl mb-4">{problem.description}</p>
      <p className="font-mono text-sm bg-ink/5 px-3 py-2 inline-block mb-4">{problem.signature}</p>
      <ul className="text-sm text-slate list-disc pl-5 mb-4">
        {problem.constraints.map((c) => (
          <li key={c}>{c}</li>
        ))}
      </ul>
      <p className="text-sm mb-6">
        Expected output: {problem.expected_output_format} · Timeout: {problem.timeout_seconds}s ·
        Hidden tests: {problem.hidden_test_count} (inputs never shown)
      </p>

      <h2 className="font-display text-2xl mb-3">Visible tests</h2>
      <ul className="space-y-2 mb-8 text-sm">
        {problem.visible_tests.map((t) => (
          <li key={t.id} className="font-mono text-xs border-t border-ink/10 pt-2">
            <span className="text-slate">{t.id}</span> — {t.description}
            {t.is_edge_case && <span className="text-accent"> (edge)</span>}
            <div>
              args={JSON.stringify(t.args)} → {JSON.stringify(t.expected)}
            </div>
          </li>
        ))}
      </ul>

      <Link to={`/problems/${problem.id}/submit`} className="btn-primary inline-block">
        Submit solution
      </Link>
    </div>
  );
}
