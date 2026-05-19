from __future__ import annotations

import math
import re
from collections import Counter

from app.models.schemas import Chunk, RetrievedChunk

TOKEN_RE = re.compile(r"[a-z0-9']+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "must",
    "of",
    "or",
    "the",
    "to",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_RE.findall(text.lower())
        if token not in STOPWORDS and len(token) > 1
    ]


def vectorize(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def cosine_similarity(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectors: list[Counter[str]] = []

    @property
    def chunks(self) -> list[Chunk]:
        return list(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._vectors.clear()

    def index(self, chunks: list[Chunk]) -> None:
        self.clear()
        self._chunks.extend(chunks)
        self._vectors.extend(vectorize(chunk.text) for chunk in chunks)

    def search(self, question: str, top_k: int) -> list[RetrievedChunk]:
        query_vector = vectorize(question)
        scored = [
            RetrievedChunk(chunk=chunk, score=round(cosine_similarity(query_vector, vector), 4))
            for chunk, vector in zip(self._chunks, self._vectors, strict=True)
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return [item for item in scored[:top_k] if item.score > 0]

