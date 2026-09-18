export function AboutPage() {
  return (
    <div className="max-w-3xl">
      <h1 className="font-display text-4xl mb-4">About the execution model</h1>
      <p className="text-slate mb-4">
        CodeTrace separates <strong>trusted algorithm visualization</strong> from{" "}
        <strong>untrusted student code evaluation</strong>.
      </p>

      <h2 className="font-display text-2xl mt-8 mb-2">Visualization</h2>
      <p className="text-slate mb-4">
        Built-in algorithms run as pure functions that emit structured events (compare, swap,
        visit, …). The React UI only replays those events — algorithm logic is not embedded in
        components.
      </p>

      <h2 className="font-display text-2xl mt-8 mb-2">Evaluation runner</h2>
      <p className="text-slate mb-4">
        Submitted Python is never executed inside the FastAPI process. A{" "}
        <code className="font-mono text-sm">Runner</code> abstraction starts a separate Python
        subprocess with a temporary directory, timeout, output size limits, and cleanup.
      </p>
      <ul className="list-disc pl-5 text-slate space-y-2 mb-4">
        <li>No <code className="font-mono text-sm">shell=True</code></li>
        <li>Controlled environment variables</li>
        <li>Process killed on timeout</li>
        <li>Designed so a Docker runner can be added later</li>
      </ul>

      <div className="border-l-4 border-accent pl-4 my-6">
        <p className="font-semibold text-ink">Important</p>
        <p className="text-slate">
          Subprocess isolation is <em>not</em> a complete security sandbox. Do not expose the
          evaluate endpoint to untrusted public internet traffic with the default local runner.
          See <code className="font-mono text-sm">RUNNER_SECURITY.md</code>.
        </p>
      </div>

      <h2 className="font-display text-2xl mt-8 mb-2">Scoring</h2>
      <p className="text-slate mb-4">
        Scores come from real test execution: correctness 70%, edge cases 20%, performance 10%.
        Hidden test inputs are never returned to the client.
      </p>

      <h2 className="font-display text-2xl mt-8 mb-2">Comparison timing</h2>
      <p className="text-slate">
        Charted timings depend on CPU load, language runtime, and machine — they are educational
        signals, not formal benchmarks.
      </p>
    </div>
  );
}
