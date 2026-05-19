import type {
  DocumentSummary,
  EvaluationSummary,
  IndexResponse,
  QueryResponse
} from "./types";

const sampleChunk = {
  id: "acme-ai-governance-policy:chunk-0004",
  document_id: "acme-ai-governance-policy",
  document_title: "Acme Analytics AI Governance Policy",
  section: "Model Evaluation",
  text:
    "AI features must be evaluated before release. Evaluation reports should include answer quality, retrieval quality, citation coverage, latency, cost estimates, known failure modes, and rollback criteria. Any system that cannot cite source evidence must decline to answer rather than invent unsupported details.",
  start_char: 1330,
  end_char: 1639,
  token_count: 42
};

const dataHandlingChunk = {
  id: "acme-ai-governance-policy:chunk-0003",
  document_id: "acme-ai-governance-policy",
  document_title: "Acme Analytics AI Governance Policy",
  section: "Data Handling",
  text:
    "Sensitive data is classified before ingestion. Documents containing regulated personal information must use redaction or approved private processing paths. Evaluation datasets should use synthetic or approved public data unless a data owner grants written approval.",
  start_char: 1042,
  end_char: 1307,
  token_count: 35
};

export function demoDocuments(): DocumentSummary[] {
  return [
    {
      id: "acme-ai-governance-policy",
      title: "Acme Analytics AI Governance Policy",
      kind: "sample",
      char_count: 1641,
      metadata: {
        domain: "enterprise-ai-governance",
        source: "synthetic-sample"
      }
    }
  ];
}

export function demoIndex(): IndexResponse {
  return {
    document_count: 1,
    chunk_count: 5,
    chunks: [sampleChunk, dataHandlingChunk]
  };
}

export function demoQuery(question: string): QueryResponse {
  return {
    question,
    answer:
      "Evaluation reports should include answer quality, retrieval quality, citation coverage, latency, cost estimates, known failure modes, and rollback criteria. [C1]",
    citations: [
      {
        id: "C1",
        chunk_id: sampleChunk.id,
        document_title: sampleChunk.document_title,
        section: sampleChunk.section,
        quote:
          "Evaluation reports should include answer quality, retrieval quality, citation coverage, latency, cost estimates, known failure modes, and rollback criteria."
      }
    ],
    retrieved_chunks: [
      {
        chunk: sampleChunk,
        score: 0.28
      },
      {
        chunk: dataHandlingChunk,
        score: 0.14
      }
    ],
    confidence: 0.68,
    metadata: {
      latency_ms: 1,
      token_estimate: 42,
      estimated_cost_usd: 0.000008,
      retrieval_top_k: 4,
      mode: "local-grounded"
    }
  };
}

export function demoEvaluation(): EvaluationSummary {
  const questions = [
    "What should the team do with secrets?",
    "How quickly should severity one incidents notify the security lead?",
    "What must be documented during AI vendor review?",
    "What should AI evaluation reports include?"
  ];
  return {
    run_id: "eval-demo",
    example_count: questions.length,
    retrieval_hit_rate: 1,
    average_citation_coverage: 1,
    average_latency_ms: 1,
    estimated_total_cost_usd: 0.000032,
    failure_count: 0,
    items: questions.map((question, index) => ({
      id: `demo-${index + 1}`,
      question,
      expected_answer: "Grounded policy answer with cited evidence.",
      actual_answer:
        index === 0
          ? "Secrets must be stored in managed secret storage and must not be committed to source control. [C1]"
          : demoQuery(question).answer,
      retrieval_hit: true,
      citation_coverage: 1,
      latency_ms: 1,
      estimated_cost_usd: 0.000008,
      failure_category: null,
      citations: demoQuery(question).citations
    }))
  };
}

