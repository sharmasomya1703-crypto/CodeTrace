import type { VizEvent } from "../types";

/** Apply mutating array events up to (and including) `upto` index. */
export function applyArrayEvents(initial: number[], events: VizEvent[], upto: number): number[] {
  const data = [...initial];
  for (let i = 0; i <= upto && i < events.length; i++) {
    const ev = events[i];
    if (ev.type === "swap" && ev.indices && ev.indices.length >= 2) {
      const [a, b] = ev.indices;
      [data[a], data[b]] = [data[b], data[a]];
    } else if (ev.type === "overwrite" && ev.index !== undefined) {
      data[ev.index] = ev.value as number;
    }
  }
  return data;
}

export function activeIndices(event: VizEvent | null): Set<number> {
  const set = new Set<number>();
  if (!event) return set;
  if (event.indices) event.indices.forEach((i) => set.add(i));
  if (event.index !== undefined) set.add(event.index);
  return set;
}
