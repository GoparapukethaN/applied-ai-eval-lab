export type DocumentSummary = {
  id: string;
  title: string;
  kind: string;
  char_count: number;
  metadata: Record<string, string>;
};

export type Chunk = {
  id: string;
  document_id: string;
  document_title: string;
  section: string;
  text: string;
  start_char: number;
  end_char: number;
  token_count: number;
};

export type IndexResponse = {
  document_count: number;
  chunk_count: number;
  chunks: Chunk[];
};

export type RetrievedChunk = {
  chunk: Chunk;
  score: number;
};

export type Citation = {
  id: string;
  chunk_id: string;
  document_title: string;
  section: string;
  quote: string;
};

export type QueryResponse = {
  question: string;
  answer: string;
  citations: Citation[];
  retrieved_chunks: RetrievedChunk[];
  confidence: number;
  metadata: {
    latency_ms: number;
    token_estimate: number;
    estimated_cost_usd: number;
    retrieval_top_k: number;
    mode: "local-grounded";
  };
};

export type EvaluationItem = {
  id: string;
  question: string;
  expected_answer: string;
  actual_answer: string;
  retrieval_hit: boolean;
  answer_fact_coverage: number;
  citation_coverage: number;
  latency_ms: number;
  estimated_cost_usd: number;
  failure_category: string | null;
  citations: Citation[];
};

export type EvaluationSummary = {
  run_id: string;
  example_count: number;
  retrieval_hit_rate: number;
  average_answer_fact_coverage: number;
  average_citation_coverage: number;
  average_latency_ms: number;
  estimated_total_cost_usd: number;
  failure_count: number;
  gate: {
    verdict: "pass" | "warn" | "fail";
    reasons: string[];
    checks: {
      name: string;
      observed: number;
      threshold: string;
      passed: boolean;
      severity: "blocker" | "warning";
      message: string;
    }[];
  };
  items: EvaluationItem[];
};

export type ExperimentConfig = {
  id: string;
  label: string;
  top_k: number;
  description: string;
};

export type ExperimentResult = {
  config: ExperimentConfig;
  summary: EvaluationSummary;
};

export type ExperimentRunResponse = {
  run_id: string;
  winner: string;
  results: ExperimentResult[];
};
