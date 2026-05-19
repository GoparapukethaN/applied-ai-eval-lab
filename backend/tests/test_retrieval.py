from app.documents.chunking import chunk_document
from app.generation.grounded import build_grounded_answer
from app.models.schemas import SourceDocument
from app.retrieval.vector_store import InMemoryVectorStore


def test_security_question_retrieves_security_chunk() -> None:
    document = SourceDocument(
        id="policy",
        title="AI Policy",
        text=(
            "# Policy\n\n"
            "## Security Controls\n\nSecrets must not be committed to source control.\n\n"
            "## Vendor Review\n\nVendors need privacy review."
        ),
    )
    store = InMemoryVectorStore()
    store.index(chunk_document(document, chunk_size=40, chunk_overlap=0))

    results = store.search("Where should secrets be stored?", top_k=2)

    assert results
    assert results[0].chunk.section == "Security Controls"
    assert results[0].score >= results[-1].score


def test_grounded_answer_returns_citations() -> None:
    document = SourceDocument(
        id="policy",
        title="AI Policy",
        text="# Policy\n\n## Incident Response\n\nSeverity one incidents notify the security lead.",
    )
    store = InMemoryVectorStore()
    store.index(chunk_document(document, chunk_size=40, chunk_overlap=0))
    results = store.search("Who is notified for severity one incidents?", top_k=1)

    response = build_grounded_answer(
        "Who is notified for severity one incidents?",
        results,
        latency_ms=12,
        top_k=1,
    )

    assert response.citations[0].id == "C1"
    assert "security lead" in response.answer.lower()
    assert response.confidence > 0


def test_grounded_answer_prefers_specific_documentation_sentence() -> None:
    document = SourceDocument(
        id="policy",
        title="AI Policy",
        text=(
            "# Policy\n\n"
            "## Vendor Review\n\n"
            "New AI vendors must complete security, privacy, and reliability review before handling data. "
            "The review must document data retention, model training usage, audit logging, and subprocessors."
        ),
    )
    store = InMemoryVectorStore()
    store.index(chunk_document(document, chunk_size=60, chunk_overlap=0))
    results = store.search("What must be documented during AI vendor review?", top_k=1)

    response = build_grounded_answer(
        "What must be documented during AI vendor review?",
        results,
        latency_ms=12,
        top_k=1,
    )

    assert "data retention" in response.answer.lower()
    assert "subprocessors" in response.answer.lower()
