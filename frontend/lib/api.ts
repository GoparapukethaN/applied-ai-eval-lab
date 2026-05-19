import type {
  DocumentSummary,
  EvaluationSummary,
  IndexResponse,
  QueryResponse
} from "./types";
import { demoDocuments, demoEvaluation, demoIndex, demoQuery } from "./demo";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

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
  if (DEMO_MODE) return Promise.resolve(demoDocuments());
  return request<DocumentSummary[]>("/documents/samples");
}

export function indexSampleDocument(documentId: string): Promise<IndexResponse> {
  if (DEMO_MODE) return Promise.resolve(demoIndex());
  return request<IndexResponse>("/documents/index", {
    method: "POST",
    body: JSON.stringify({ document_ids: [documentId] })
  });
}

export function askQuestion(question: string): Promise<QueryResponse> {
  if (DEMO_MODE) return Promise.resolve(demoQuery(question));
  return request<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({ question })
  });
}

export function runEvaluation(): Promise<EvaluationSummary> {
  if (DEMO_MODE) return Promise.resolve(demoEvaluation());
  return request<EvaluationSummary>("/evaluation/run", {
    method: "POST",
    body: JSON.stringify({})
  });
}
