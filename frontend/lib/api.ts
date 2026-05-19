import type {
  DocumentSummary,
  EvaluationSummary,
  IndexResponse,
  QueryResponse
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getSampleDocuments(): Promise<DocumentSummary[]> {
  return request<DocumentSummary[]>("/documents/samples");
}

export function indexSampleDocument(documentId: string): Promise<IndexResponse> {
  return request<IndexResponse>("/documents/index", {
    method: "POST",
    body: JSON.stringify({ document_ids: [documentId] })
  });
}

export function askQuestion(question: string): Promise<QueryResponse> {
  return request<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({ question })
  });
}

export function runEvaluation(): Promise<EvaluationSummary> {
  return request<EvaluationSummary>("/evaluation/run", {
    method: "POST",
    body: JSON.stringify({})
  });
}

