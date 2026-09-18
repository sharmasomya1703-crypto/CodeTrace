/// <reference lib="webworker" />

export type WorkerRequest =
  | { type: "ping" }
  | {
      type: "compareLocal";
      sizes: number[];
      labelA: string;
      labelB: string;
    };

export type WorkerResponse =
  | { type: "pong" }
  | {
      type: "compareLocalResult";
      points: Array<{ size: number; aMs: number; bMs: number }>;
    };

/** Lightweight main-thread offload helper for demo timings (not a formal benchmark). */
function busyWork(n: number, factor: number): number {
  let acc = 0;
  for (let i = 0; i < n * factor; i++) {
    acc += (i % 7) * (i % 5);
  }
  return acc;
}

self.onmessage = (ev: MessageEvent<WorkerRequest>) => {
  const msg = ev.data;
  if (msg.type === "ping") {
    (self as DedicatedWorkerGlobalScope).postMessage({ type: "pong" } satisfies WorkerResponse);
    return;
  }
  if (msg.type === "compareLocal") {
    const points = msg.sizes.map((size) => {
      const t0 = performance.now();
      busyWork(size, 20);
      const aMs = performance.now() - t0;
      const t1 = performance.now();
      busyWork(size, 35);
      const bMs = performance.now() - t1;
      return { size, aMs, bMs };
    });
    (self as DedicatedWorkerGlobalScope).postMessage({
      type: "compareLocalResult",
      points,
    } satisfies WorkerResponse);
  }
};
