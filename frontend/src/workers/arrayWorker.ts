/// <reference lib="webworker" />

export type ArrayWorkerRequest = {
  type: "generate";
  size: number;
  mode: "random" | "sorted" | "reverse";
  seed?: number;
};

export type ArrayWorkerResponse = {
  type: "array";
  array: number[];
};

function mulberry32(a: number) {
  return function () {
    let t = (a += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

self.onmessage = (ev: MessageEvent<ArrayWorkerRequest>) => {
  const { size, mode, seed = 42 } = ev.data;
  let array: number[] = [];
  if (mode === "sorted") {
    array = Array.from({ length: size }, (_, i) => i);
  } else if (mode === "reverse") {
    array = Array.from({ length: size }, (_, i) => size - 1 - i);
  } else {
    const rand = mulberry32(seed);
    array = Array.from({ length: size }, () => Math.floor(rand() * 100));
  }
  (self as DedicatedWorkerGlobalScope).postMessage({ type: "array", array } satisfies ArrayWorkerResponse);
};
