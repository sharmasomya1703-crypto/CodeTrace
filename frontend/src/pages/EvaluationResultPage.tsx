import { Link, useLocation, useParams } from "react-router-dom";
import type { EvaluationResult } from "../types";

export function EvaluationResultPage() {
  const { id = "" } = useParams();
  const location = useLocation();
  const result = (location.state as { result?: EvaluationResult } | null)?.result;

  if (!result) {
    return (
      <div>
        <p className="text-slate mb-4">No evaluation result in memory.</p>
        <Link to={`/problems/${id}/submit`} className="btn-primary inline-block">
          Submit again
        </Link>
      </div>
    );
  }

  if (!result.ok) {
    return (
      <div>
        <h1 className="font-display text-4xl mb-2">Evaluation failed</h1>
        <p className="text-accent">{result.error}</p>
      </div>
    );
  }

  const scores = result.scores!;

  return (
    <div>
      <h1 className="font-display text-4xl mb-2">Evaluation result</h1>
      <p className="text-slate mb-6">Problem: {result.problem_id}</p>

      <div className="grid sm:grid-cols-4 gap-4 mb-8">
        {[
          ["Overall", scores.overall],
          ["Correctness", scores.correctness],
          ["Edge cases", scores.edge_cases],
          ["Performance", scores.performance],
        ].map(([label, value]) => (
          <div key={String(label)} className="border-t-2 border-ink pt-3">
            <p className="text-sm text-slate">{label}</p>
            <p className="font-display text-3xl">{value}%</p>
          </div>
        ))}
      </div>

      <p className="text-sm text-slate mb-2">
        Weights: correctness {scores.weights.correctness * 100}% · edge{" "}
        {scores.weights.edge_cases * 100}% · performance {scores.weights.performance * 100}%
      </p>
      <p className="text-sm mb-6">
        Wall time: {result.wall_time_ms} ms
        {result.timed_out ? " · Timed out" : ""}
        {result.error ? ` · ${result.error}` : ""}
      </p>

      <h2 className="font-display text-2xl mb-3">Visible tests</h2>
      <ul className="space-y-3 mb-8">
        {result.visible_tests?.map((t) => (
          <li key={t.test_id} className="border-t border-ink/10 pt-3 text-sm">
            <span className={t.passed ? "text-sea" : "text-accent"}>
              {t.passed ? "PASS" : "FAIL"}
            </span>{" "}
            <span className="font-mono">{t.test_id}</span> · {t.runtime_ms} ms
            {t.timed_out && " · timeout"}
            {t.exception && <div className="text-accent font-mono text-xs mt-1">{t.exception}</div>}
            {!t.passed && (
              <div className="font-mono text-xs mt-1">
                expected: {JSON.stringify(t.expected)}
                <br />
                actual: {JSON.stringify(t.actual)}
              </div>
            )}
          </li>
        ))}
      </ul>

      <h2 className="font-display text-2xl mb-2">Hidden tests</h2>
      <p className="text-slate mb-6">
        {result.hidden_summary?.passed}/{result.hidden_summary?.total} passed (inputs not revealed)
      </p>

      <p className="text-xs text-slate max-w-2xl mb-6">{result.security_note}</p>
      <Link to={`/problems/${id}/submit`} className="btn-secondary inline-block">
        Edit & resubmit
      </Link>
    </div>
  );
}
