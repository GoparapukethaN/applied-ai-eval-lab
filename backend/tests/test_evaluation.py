from app.evaluation.scoring import citation_coverage, summarize_evaluation
from app.models.schemas import (
    Chunk,
    Citation,
    EvaluationExample,
    QueryMetadata,
    QueryResponse,
    RetrievedChunk,
)


def _response() -> QueryResponse:
    chunk = Chunk(
        id="doc:chunk-1",
        document_id="doc",
        document_title="Policy",
        section="Security",
        text="Secrets must not be committed to source control.",
        start_char=0,
        end_char=49,
        token_count=8,
    )
    return QueryResponse(
        question="What about secrets?",
        answer="Secrets must not be committed. [C1]",
        citations=[
            Citation(
                id="C1",
                chunk_id=chunk.id,
                document_title=chunk.document_title,
                section=chunk.section,
                quote="Secrets must not be committed to source control.",
            )
        ],
        retrieved_chunks=[RetrievedChunk(chunk=chunk, score=0.7)],
        confidence=0.6,
        metadata=QueryMetadata(
            latency_ms=10,
            token_estimate=8,
            estimated_cost_usd=0.000001,
            retrieval_top_k=1,
            mode="local-grounded",
        ),
    )


def test_citation_coverage_counts_cited_retrieved_chunks() -> None:
    assert citation_coverage(_response()) == 1.0


def test_summarize_evaluation_computes_quality_metrics() -> None:
    example = EvaluationExample(
        id="secrets",
        question="What about secrets?",
        expected_answer="Do not commit secrets.",
        expected_chunk_keywords=["source control"],
    )
    summary = summarize_evaluation([example], [_response()])

    assert summary.example_count == 1
    assert summary.retrieval_hit_rate == 1.0
    assert summary.failure_count == 0
    assert summary.average_latency_ms == 10

