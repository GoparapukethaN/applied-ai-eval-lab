from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.schemas import Chunk, SourceDocument

SPACE_RE = re.compile(r"[ \t]+")
TOKEN_RE = re.compile(r"[A-Za-z0-9']+")


@dataclass(frozen=True)
class Section:
    title: str
    text: str
    start_char: int


def normalize_text(text: str) -> str:
    lines = [SPACE_RE.sub(" ", line).strip() for line in text.splitlines()]
    normalized = "\n".join(lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def count_tokens(text: str) -> int:
    return len(TOKEN_RE.findall(text))


def split_sections(text: str) -> list[Section]:
    normalized = normalize_text(text)
    sections: list[Section] = []
    current_title = "Overview"
    current_lines: list[str] = []
    current_start = 0
    cursor = 0

    for raw_line in normalized.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            if current_lines:
                sections.append(
                    Section(
                        title=current_title,
                        text="\n".join(current_lines).strip(),
                        start_char=current_start,
                    )
                )
                current_lines = []
            current_title = line.lstrip("#").strip() or "Untitled"
            current_start = cursor + len(raw_line) + 1
        elif line:
            if not current_lines:
                current_start = cursor
            current_lines.append(line)
        cursor += len(raw_line) + 1

    if current_lines:
        sections.append(
            Section(
                title=current_title,
                text="\n".join(current_lines).strip(),
                start_char=current_start,
            )
        )
    return sections


def _window_text(words: list[str], start: int, end: int) -> str:
    return " ".join(words[start:end]).strip()


def chunk_document(
    document: SourceDocument,
    chunk_size: int = 900,
    chunk_overlap: int = 120,
) -> list[Chunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[Chunk] = []
    chunk_index = 0
    for section in split_sections(document.text):
        words = section.text.split()
        if not words:
            continue
        step = max(1, chunk_size - chunk_overlap)
        for start_word in range(0, len(words), step):
            end_word = min(len(words), start_word + chunk_size)
            text = _window_text(words, start_word, end_word)
            if not text:
                continue
            start_char = section.start_char + len(" ".join(words[:start_word]))
            end_char = start_char + len(text)
            chunks.append(
                Chunk(
                    id=f"{document.id}:chunk-{chunk_index:04d}",
                    document_id=document.id,
                    document_title=document.title,
                    section=section.title,
                    text=text,
                    start_char=start_char,
                    end_char=end_char,
                    token_count=count_tokens(text),
                )
            )
            chunk_index += 1
            if end_word >= len(words):
                break
    return chunks


def chunk_documents(
    documents: list[SourceDocument],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size, chunk_overlap))
    return chunks

