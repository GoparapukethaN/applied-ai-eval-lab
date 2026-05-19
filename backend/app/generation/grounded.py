from __future__ import annotations

import re

from app.models.schemas import Citation, QueryMetadata, QueryResponse, RetrievedChunk

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _best_sentence(question: str, text: str) -> str:
    question_terms = {term.lower() for term in re.findall(r"[A-Za-z0-9']+", question)}
    sentences = [sentence.strip() for sentence in SENTENCE_RE.split(text) if sentence.strip()]
    if not sentences:
        return text[:280].strip()
    ranked = sorted(
        sentences,
        key=lambda sentence: len(question_terms & set(re.findall(r"[a-z0-9']+", sentence.lower()))),
        reverse=True,
    )
    return ranked[0][:360].strip()


def build_grounded_answer(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
    latency_ms: int,
    top_k: int,
) -> QueryResponse:
    best_score = max((item.score for item in retrieved_chunks), default=0.0)
    useful_chunks: list[RetrievedChunk] = []
    if retrieved_chunks and best_score >= 0.06:
        useful_chunks.append(retrieved_chunks[0])
        secondary_threshold = max(0.12, best_score * 0.55)
        useful_chunks.extend(
            item
            for item in retrieved_chunks[1:]
            if item.score >= secondary_threshold and item.chunk.id != retrieved_chunks[0].chunk.id
        )
    if not useful_chunks:
        return QueryResponse(
            question=question,
            answer=(
                "I do not have enough retrieved evidence to answer this question "
                "from the indexed documents."
            ),
            citations=[],
            retrieved_chunks=retrieved_chunks,
            confidence=0.0,
            metadata=QueryMetadata(
                latency_ms=latency_ms,
                token_estimate=0,
                estimated_cost_usd=0.0,
                retrieval_top_k=top_k,
                mode="local-grounded",
            ),
        )

    citations: list[Citation] = []
    answer_parts: list[str] = []
    for index, item in enumerate(useful_chunks[:2], start=1):
        quote = _best_sentence(question, item.chunk.text)
        citation_id = f"C{index}"
        citations.append(
            Citation(
                id=citation_id,
                chunk_id=item.chunk.id,
                document_title=item.chunk.document_title,
                section=item.chunk.section,
                quote=quote,
            )
        )
        answer_parts.append(f"{quote} [{citation_id}]")

    token_estimate = sum(item.chunk.token_count for item in useful_chunks[:top_k])
    confidence = min(0.95, round(best_score * 2.4, 2))
    return QueryResponse(
        question=question,
        answer=" ".join(answer_parts),
        citations=citations,
        retrieved_chunks=retrieved_chunks,
        confidence=confidence,
        metadata=QueryMetadata(
            latency_ms=latency_ms,
            token_estimate=token_estimate,
            estimated_cost_usd=round(token_estimate * 0.0000002, 6),
            retrieval_top_k=top_k,
            mode="local-grounded",
        ),
    )
