import type { AlgorithmMeta, AlgorithmResult, EvaluationResult, ProblemSummary } from "../types";

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; version: string; eval_enabled: boolean }>("/api/health"),
  algorithms: () => request<AlgorithmMeta[]>("/api/algorithms"),
  algorithm: (id: string) => request<AlgorithmMeta>(`/api/algorithms/${id}`),
  visualize: (algorithm: string, data: Record<string, unknown>) =>
    request<AlgorithmResult>("/api/visualize", {
      method: "POST",
      body: JSON.stringify({ algorithm, data }),
    }),
  compare: (algorithms: [string, string], sizes: number[], data?: Record<string, unknown>) =>
    request<{
      sizes?: number[];
      points: Array<{
        input_size: number;
        disclaimer: string;
        a: Record<string, unknown>;
        b: Record<string, unknown>;
      }>;
      disclaimer: string;
    }>("/api/compare", {
      method: "POST",
      body: JSON.stringify({ algorithms, sizes, data: data ?? {} }),
    }),
  problems: () => request<ProblemSummary[]>("/api/problems"),
  problem: (id: string) => request<ProblemSummary>(`/api/problems/${id}`),
  evaluate: (problem_id: string, source: string) =>
    request<EvaluationResult>("/api/evaluate", {
      method: "POST",
      body: JSON.stringify({ problem_id, source }),
    }),
  generateArray: (size: number, mode: string, seed?: number) => {
    const params = new URLSearchParams({ size: String(size), mode });
    if (seed !== undefined) params.set("seed", String(seed));
    return request<{ array: number[] }>(`/api/generate-array?${params}`);
  },
};
