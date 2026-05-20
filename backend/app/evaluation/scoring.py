from __future__ import annotations

from uuid import uuid4

from app.models.schemas import (
    EvaluationExample,
    EvaluationGate,
    EvaluationGateCheck,
    EvaluationItem,
    EvaluationSummary,
    QueryResponse,
)

MIN_RETRIEVAL_HIT_RATE = 0.75
MIN_CITATION_COVERAGE = 0.75
MAX_FAILURE_COUNT = 0
MAX_AVERAGE_LATENCY_MS = 2_000


DEFAULT_EVAL_EXAMPLES = [
    EvaluationExample(
        id="security-secrets",
        question="What should the team do with secrets?",
        expected_answer="Secrets must be stored in managed secret storage and not committed.",
        expected_chunk_keywords=["secrets", "source control"],
    ),
    EvaluationExample(
        id="incident-sev-one",
        question="How quickly should severity one incidents notify the security lead?",
        expected_answer="The security lead should be notified within fifteen minutes.",
        expected_chunk_keywords=["severity one", "fifteen minutes"],
    ),
    EvaluationExample(
        id="vendor-review",
        question="What must be documented during AI vendor review?",
        expected_answer="Data retention, model training usage, regional processing, audit logging, subprocessors, and service-level commitments.",
        expected_chunk_keywords=["data retention", "model training", "subprocessors"],
    ),
    EvaluationExample(
        id="evaluation-report",
        question="What should AI evaluation reports include?",
        expected_answer="Answer quality, retrieval quality, citation coverage, latency, cost estimates, known failure modes, and rollback criteria.",
        expected_chunk_keywords=["answer quality", "citation coverage", "rollback"],
    ),
]


def citation_coverage(response: QueryResponse) -> float:
    if not response.citations:
        return 0.0
    cited_chunk_ids = {citation.chunk_id for citation in response.citations}
    retrieved_chunk_ids = {item.chunk.id for item in response.retrieved_chunks}
    if not retrieved_chunk_ids:
        return 0.0
    return round(len(cited_chunk_ids & retrieved_chunk_ids) / len(cited_chunk_ids), 3)


def retrieval_hit(example: EvaluationExample, response: QueryResponse) -> bool:
    searchable = " ".join(item.chunk.text.lower() for item in response.retrieved_chunks)
    return any(keyword.lower() in searchable for keyword in example.expected_chunk_keywords)


def classify_failure(example: EvaluationExample, response: QueryResponse) -> str | None:
    if not response.citations:
        return "no_citation"
    if not retrieval_hit(example, response):
        return "missed_relevant_context"
    if response.confidence < 0.15:
        return "low_confidence"
    return None


def summarize_evaluation(
    examples: list[EvaluationExample],
    responses: list[QueryResponse],
) -> EvaluationSummary:
    items: list[EvaluationItem] = []
    for example, response in zip(examples, responses, strict=True):
        hit = retrieval_hit(example, response)
        failure = classify_failure(example, response)
        items.append(
            EvaluationItem(
                id=example.id,
                question=example.question,
                expected_answer=example.expected_answer,
                actual_answer=response.answer,
                retrieval_hit=hit,
                citation_coverage=citation_coverage(response),
                latency_ms=response.metadata.latency_ms,
                estimated_cost_usd=response.metadata.estimated_cost_usd,
                failure_category=failure,
                citations=response.citations,
            )
        )

    example_count = len(items)
    if example_count == 0:
        return EvaluationSummary(
            run_id=f"eval-{uuid4().hex[:8]}",
            example_count=0,
            retrieval_hit_rate=0.0,
            average_citation_coverage=0.0,
            average_latency_ms=0.0,
            estimated_total_cost_usd=0.0,
            failure_count=0,
            gate=_build_gate(
                example_count=0,
                retrieval_hit_rate=0.0,
                citation_coverage=0.0,
                average_latency_ms=0.0,
                failure_count=0,
            ),
            items=[],
        )

    retrieval_hit_rate = round(sum(1 for item in items if item.retrieval_hit) / example_count, 3)
    citation_coverage_score = round(
        sum(item.citation_coverage for item in items) / example_count,
        3,
    )
    average_latency_ms = round(sum(item.latency_ms for item in items) / example_count, 1)
    failure_count = sum(1 for item in items if item.failure_category)

    return EvaluationSummary(
        run_id=f"eval-{uuid4().hex[:8]}",
        example_count=example_count,
        retrieval_hit_rate=retrieval_hit_rate,
        average_citation_coverage=citation_coverage_score,
        average_latency_ms=average_latency_ms,
        estimated_total_cost_usd=round(sum(item.estimated_cost_usd for item in items), 6),
        failure_count=failure_count,
        gate=_build_gate(
            example_count=example_count,
            retrieval_hit_rate=retrieval_hit_rate,
            citation_coverage=citation_coverage_score,
            average_latency_ms=average_latency_ms,
            failure_count=failure_count,
        ),
        items=items,
    )


def _build_gate(
    *,
    example_count: int,
    retrieval_hit_rate: float,
    citation_coverage: float,
    average_latency_ms: float,
    failure_count: int,
) -> EvaluationGate:
    checks: list[EvaluationGateCheck] = [
        EvaluationGateCheck(
            name="eval_examples",
            observed=float(example_count),
            threshold="> 0",
            passed=example_count > 0,
            severity="blocker",
            message="The gate needs at least one curated evaluation example.",
        ),
        EvaluationGateCheck(
            name="retrieval_hit_rate",
            observed=retrieval_hit_rate,
            threshold=f">= {MIN_RETRIEVAL_HIT_RATE}",
            passed=retrieval_hit_rate >= MIN_RETRIEVAL_HIT_RATE,
            severity="blocker",
            message="Retrieved evidence should cover the expected source facts.",
        ),
        EvaluationGateCheck(
            name="citation_coverage",
            observed=citation_coverage,
            threshold=f">= {MIN_CITATION_COVERAGE}",
            passed=citation_coverage >= MIN_CITATION_COVERAGE,
            severity="blocker",
            message="Answers should cite the chunks they use.",
        ),
        EvaluationGateCheck(
            name="failure_count",
            observed=float(failure_count),
            threshold=f"<= {MAX_FAILURE_COUNT}",
            passed=failure_count <= MAX_FAILURE_COUNT,
            severity="blocker",
            message="Known failure categories should be resolved before release.",
        ),
        EvaluationGateCheck(
            name="average_latency_ms",
            observed=average_latency_ms,
            threshold=f"<= {MAX_AVERAGE_LATENCY_MS}",
            passed=average_latency_ms <= MAX_AVERAGE_LATENCY_MS,
            severity="warning",
            message="Average latency should stay inside the review budget.",
        ),
    ]
    failed_checks = [check for check in checks if not check.passed]
    reasons = [check.message for check in failed_checks]
    if any(check.severity == "blocker" for check in failed_checks):
        verdict = "fail"
    elif failed_checks:
        verdict = "warn"
    else:
        verdict = "pass"

    return EvaluationGate(verdict=verdict, reasons=reasons, checks=checks)
