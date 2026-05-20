import type {
  DocumentSummary,
  EvaluationSummary,
  ExperimentRunResponse,
  IndexResponse,
  QueryResponse
} from "./types";

const sampleChunk = {
  id: "acme-ai-governance-policy:chunk-0005",
  document_id: "acme-ai-governance-policy",
  document_title: "Acme Analytics AI Governance Policy",
  section: "Model Evaluation",
  text:
    "AI features must be evaluated before release. Evaluation reports should include answer quality, retrieval quality, citation coverage, latency, cost estimates, known failure modes, and rollback criteria. Any system that cannot cite source evidence must decline to answer rather than invent unsupported details.",
  start_char: 1330,
  end_char: 1639,
  token_count: 42
};

const securityChunk = {
  id: "acme-ai-governance-policy:chunk-0001",
  document_id: "acme-ai-governance-policy",
  document_title: "Acme Analytics AI Governance Policy",
  section: "Security Controls",
  text:
    "All customer documents must be encrypted in transit and at rest. Access to indexed documents is limited to approved workspace members. Production systems must log document ingestion events, query events, and administrative changes. Secrets must be stored in managed secret storage and must not be committed to source control.",
  start_char: 55,
  end_char: 425,
  token_count: 47
};

const incidentChunk = {
  id: "acme-ai-governance-policy:chunk-0002",
  document_id: "acme-ai-governance-policy",
  document_title: "Acme Analytics AI Governance Policy",
  section: "Incident Response",
  text:
    "The incident response process starts with triage, severity assignment, and owner selection. Severity one incidents require notification to the security lead within fifteen minutes. The response team must preserve logs, document customer impact, apply containment, and complete a written post-incident review within five business days.",
  start_char: 427,
  end_char: 781,
  token_count: 47
};

const vendorChunk = {
  id: "acme-ai-governance-policy:chunk-0003",
  document_id: "acme-ai-governance-policy",
  document_title: "Acme Analytics AI Governance Policy",
  section: "Vendor Review",
  text:
    "New AI vendors must complete security, privacy, and reliability review before handling internal or customer data. The review must document data retention, model training usage, regional processing, audit logging, subprocessors, and service-level commitments.",
  start_char: 783,
  end_char: 1040,
  token_count: 34
};

const dataHandlingChunk = {
  id: "acme-ai-governance-policy:chunk-0004",
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
    chunks: [securityChunk, incidentChunk, vendorChunk, dataHandlingChunk, sampleChunk]
  };
}

export function demoUpload(): IndexResponse {
  return {
    document_count: 1,
    chunk_count: 1,
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
  const loweredQuestion = question.toLowerCase();
  const selected =
    loweredQuestion.includes("secret") || loweredQuestion.includes("source control")
      ? {
          chunk: securityChunk,
          answer:
            "Secrets must be stored in managed secret storage and must not be committed to source control. [C1]",
          quote:
            "Secrets must be stored in managed secret storage and must not be committed to source control.",
          score: 0.42
        }
      : loweredQuestion.includes("severity") || loweredQuestion.includes("incident")
        ? {
            chunk: incidentChunk,
            answer:
              "Severity one incidents require notification to the security lead within fifteen minutes. [C1]",
            quote:
              "Severity one incidents require notification to the security lead within fifteen minutes.",
            score: 0.38
          }
        : loweredQuestion.includes("vendor") || loweredQuestion.includes("review")
          ? {
              chunk: vendorChunk,
              answer:
                "The review must document data retention, model training usage, regional processing, audit logging, subprocessors, and service-level commitments. [C1]",
              quote:
                "The review must document data retention, model training usage, regional processing, audit logging, subprocessors, and service-level commitments.",
              score: 0.35
            }
          : {
              chunk: sampleChunk,
              answer:
                "Evaluation reports should include answer quality, retrieval quality, citation coverage, latency, cost estimates, known failure modes, and rollback criteria. [C1]",
              quote:
                "Evaluation reports should include answer quality, retrieval quality, citation coverage, latency, cost estimates, known failure modes, and rollback criteria.",
              score: 0.28
            };

  return {
    question,
    answer: selected.answer,
    citations: [
      {
        id: "C1",
        chunk_id: selected.chunk.id,
        document_title: selected.chunk.document_title,
        section: selected.chunk.section,
        quote: selected.quote
      }
    ],
    retrieved_chunks: [
      {
        chunk: selected.chunk,
        score: selected.score
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

function demoEvaluationAnswer(index: number, question: string): string {
  const answers = [
    "Secrets must be stored in managed secret storage and must not be committed to source control. [C1]",
    "Severity one incidents require notification to the security lead within fifteen minutes. [C1]",
    "The review must document data retention, model training usage, regional processing, audit logging, subprocessors, and service-level commitments. [C1]",
    demoQuery(question).answer
  ];
  return answers[index] ?? demoQuery(question).answer;
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
    average_answer_fact_coverage: 1,
    average_citation_coverage: 1,
    average_latency_ms: 1,
    estimated_total_cost_usd: 0.000032,
    failure_count: 0,
    gate: {
      verdict: "pass",
      reasons: [],
      checks: [
        {
          name: "eval_examples",
          observed: questions.length,
          threshold: "> 0",
          passed: true,
          severity: "blocker",
          message: "The gate needs at least one curated evaluation example."
        },
        {
          name: "retrieval_hit_rate",
          observed: 1,
          threshold: ">= 0.75",
          passed: true,
          severity: "blocker",
          message: "Retrieved evidence should cover the expected source facts."
        },
        {
          name: "citation_coverage",
          observed: 1,
          threshold: ">= 0.75",
          passed: true,
          severity: "blocker",
          message: "Answers should cite the chunks they use."
        },
        {
          name: "answer_fact_coverage",
          observed: 1,
          threshold: ">= 0.6",
          passed: true,
          severity: "blocker",
          message: "Answers should include the expected curated answer facts."
        },
        {
          name: "failure_count",
          observed: 0,
          threshold: "<= 0",
          passed: true,
          severity: "blocker",
          message: "Known failure categories should be resolved before release."
        },
        {
          name: "average_latency_ms",
          observed: 1,
          threshold: "<= 2000",
          passed: true,
          severity: "warning",
          message: "Average latency should stay inside the review budget."
        }
      ]
    },
    items: questions.map((question, index) => ({
      id: `demo-${index + 1}`,
      question,
      expected_answer: "Grounded policy answer with cited evidence.",
      actual_answer: demoEvaluationAnswer(index, question),
      retrieval_hit: true,
      answer_fact_coverage: 1,
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
