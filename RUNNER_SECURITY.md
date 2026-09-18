# Runner Security

CodeTrace evaluates student Python by running it **outside** the FastAPI process.

## Design

```text
FastAPI / CLI
    │
    ▼
Runner.run(solution, problem, limits) -> ExecutionResult
    │
    ├── SubprocessLocalRunner  (default, local/dev)
    └── DockerRunner           (future)
```

The API never calls `exec`, `eval`, or `importlib` on submitted source inside its own process.

## SubprocessLocalRunner controls

- Temporary working directory per run
- Strict wall-clock timeout; process group terminated on timeout
- Controlled environment variables (minimal `PATH`, no secrets)
- Limited stdin/stdout/stderr capture sizes
- `subprocess.Popen` with argument list — **never** `shell=True`
- Best-effort resource limits via `resource` on Unix
- Cleanup of temp directories after execution

## Important limitations

**Subprocess isolation is not a complete security sandbox.**

A malicious solution may still:

- Consume CPU / memory until limits apply
- Attempt filesystem access within the temp dir / process permissions
- Attempt network access if the OS user can
- Attempt to escape via OS-level bugs

Do **not** expose the evaluate endpoint to untrusted public internet traffic with the default local runner.

## Recommended deployments

| Environment | Recommendation |
|-------------|----------------|
| Local learning / classroom laptop | SubprocessLocalRunner OK |
| Shared campus server | Prefer Docker runner + low privileges |
| Public internet | Require hardened sandbox (gVisor/Firecracker/etc.) + auth + rate limits |

## Configuration

- `CODETRACE_ENABLE_EVAL=true` — enable evaluate API (default `true` for local compose)
- `CODETRACE_RUNNER=subprocess` — runner backend
- `CODETRACE_MAX_OUTPUT_BYTES` — stdout/stderr cap
- `CODETRACE_DEFAULT_TIMEOUT` — fallback timeout seconds

Default documentation and About page must state these limits clearly. Never claim the runner is safe for arbitrary untrusted public code.
