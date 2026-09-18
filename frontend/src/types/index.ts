export type VizEvent = {
  type: string;
  indices?: number[];
  index?: number;
  values?: number[];
  value?: number;
  previous?: number;
  node?: string;
  nodes?: string[];
  queue?: string[];
  stack?: string[];
  from?: string;
  to?: string;
  weight?: number;
  old_distance?: number | null;
  new_distance?: number;
  role?: string;
  result?: unknown;
  metrics?: Record<string, number>;
  target?: number;
  structure?: string;
  distance?: number;
};

export type AlgorithmMeta = {
  id: string;
  title: string;
  category: string;
  description: string;
  pseudocode: string;
  time_complexity: string;
  space_complexity: string;
  stable: boolean | null;
  in_place: boolean | null;
  use_cases: string[];
  common_mistakes: string[];
};

export type AlgorithmResult = {
  algorithm: string;
  input: unknown;
  events: VizEvent[];
  result: unknown;
  metrics: Record<string, number>;
};

export type ProblemSummary = {
  id: string;
  title: string;
  description: string;
  function_name: string;
  signature: string;
  constraints: string[];
  timeout_seconds: number;
  expected_output_format: string;
  visible_tests: Array<{
    id: string;
    description: string;
    args: unknown[];
    kwargs: Record<string, unknown>;
    expected: unknown;
    is_edge_case: boolean;
  }>;
  hidden_test_count: number;
};

export type EvaluationResult = {
  ok: boolean;
  problem_id?: string;
  success?: boolean;
  timed_out?: boolean;
  error?: string;
  wall_time_ms?: number;
  scores?: {
    correctness: number;
    edge_cases: number;
    performance: number;
    overall: number;
    weights: Record<string, number>;
  };
  visible_tests?: Array<{
    test_id: string;
    passed: boolean;
    runtime_ms: number;
    timed_out: boolean;
    exception: string | null;
    expected: unknown;
    actual: unknown;
    is_edge_case: boolean;
  }>;
  hidden_summary?: { passed: number; failed: number; total: number };
  security_note?: string;
};
