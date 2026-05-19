import type {
  DocumentSummary,
  EvaluationSummary,
  ExperimentRunResponse,
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

export function demoUpload(): IndexResponse {
  return {
    document_count: 1,
    chunk_count: 4,
    chunks: [
      {
        ...sampleChunk,
        id: "uploaded-policy:chunk-0001",
        document_id: "uploaded-policy",
        document_title: "Uploaded Policy Brief"
      }
    ]
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

export function demoExperiments(): ExperimentRunResponse {
  const base = demoEvaluation();
  return {
    run_id: "experiment-demo",
    winner: "balanced",
    results: [
      {
        config: {
          id: "focused",
          label: "Focused Retrieval",
          top_k: 2,
          description: "Prioritizes the strongest chunks to reduce noisy citations."
        },
        summary: {
          ...base,
          run_id: "eval-focused",
          average_citation_coverage: 1,
          average_latency_ms: 1.1
        }
      },
      {
        config: {
          id: "balanced",
          label: "Balanced Retrieval",
          top_k: 4,
          description: "Default setting for quality, latency, and evidence coverage."
        },
        summary: {
          ...base,
          run_id: "eval-balanced",
          average_citation_coverage: 1,
          average_latency_ms: 1
        }
      },
      {
        config: {
          id: "broad",
          label: "Broad Retrieval",
          top_k: 6,
          description: "Pulls more context for ambiguous review workflows."
        },
        summary: {
          ...base,
          run_id: "eval-broad",
          average_citation_coverage: 0.92,
          average_latency_ms: 1.6
        }
      }
    ]
  };
}
