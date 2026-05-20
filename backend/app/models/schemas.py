from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    checked_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class SourceDocument(BaseModel):
    id: str
    title: str
    kind: Literal["sample", "uploaded"] = "sample"
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)


class DocumentSummary(BaseModel):
    id: str
    title: str
    kind: str
    char_count: int
    metadata: dict[str, str] = Field(default_factory=dict)


class Chunk(BaseModel):
    id: str
    document_id: str
    document_title: str
    section: str
    text: str
    start_char: int
    end_char: int
    token_count: int


class IndexRequest(BaseModel):
    document_ids: list[str] = Field(default_factory=list)
    custom_documents: list[SourceDocument] = Field(default_factory=list)
    chunk_size: int | None = None
    chunk_overlap: int | None = None


class IndexResponse(BaseModel):
    document_count: int
    chunk_count: int
    chunks: list[Chunk]


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1_000)
    top_k: int | None = Field(default=None, ge=1, le=12)


class RetrievedChunk(BaseModel):
    chunk: Chunk
    score: float


class Citation(BaseModel):
    id: str
    chunk_id: str
    document_title: str
    section: str
    quote: str


class QueryMetadata(BaseModel):
    latency_ms: int
    token_estimate: int
    estimated_cost_usd: float
    retrieval_top_k: int
    mode: Literal["local-grounded"]


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    confidence: float
    metadata: QueryMetadata


class EvaluationExample(BaseModel):
    id: str
    question: str
    expected_answer: str
    expected_chunk_keywords: list[str]


class EvaluationRequest(BaseModel):
    examples: list[EvaluationExample] | None = None


class EvaluationItem(BaseModel):
    id: str
    question: str
    expected_answer: str
    actual_answer: str
    retrieval_hit: bool
    answer_fact_coverage: float
    citation_coverage: float
    latency_ms: int
    estimated_cost_usd: float
    failure_category: str | None = None
    citations: list[Citation]


class EvaluationGateCheck(BaseModel):
    name: str
    observed: float
    threshold: str
    passed: bool
    severity: Literal["blocker", "warning"]
    message: str


class EvaluationGate(BaseModel):
    verdict: Literal["pass", "warn", "fail"]
    reasons: list[str]
    checks: list[EvaluationGateCheck]


class EvaluationSummary(BaseModel):
    run_id: str
    example_count: int
    retrieval_hit_rate: float
    average_answer_fact_coverage: float
    average_citation_coverage: float
    average_latency_ms: float
    estimated_total_cost_usd: float
    failure_count: int
    gate: EvaluationGate
    items: list[EvaluationItem]


class ExperimentConfig(BaseModel):
    id: str
    label: str
    top_k: int = Field(ge=1, le=12)
    description: str


class ExperimentResult(BaseModel):
    config: ExperimentConfig
    summary: EvaluationSummary


class ExperimentRunResponse(BaseModel):
    run_id: str
    winner: str
    results: list[ExperimentResult]


class ReportSummary(BaseModel):
    kind: str
    run_id: str
    filename: str
    markdown_filename: str | None = None
    created_at: datetime
