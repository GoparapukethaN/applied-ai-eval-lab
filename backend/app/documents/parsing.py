from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from app.core.errors import bad_request
from app.models.schemas import SourceDocument

TEXT_TYPES = {"text/plain", "text/markdown", "application/octet-stream"}


def parse_uploaded_document(filename: str, content_type: str | None, content: bytes) -> SourceDocument:
    if not content:
        raise bad_request("Uploaded file is empty.", "empty_upload")

    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf" or content_type == "application/pdf":
        text = _parse_pdf(content)
    elif suffix in {".txt", ".md"} or content_type in TEXT_TYPES:
        text = _parse_text(content)
    else:
        raise bad_request(
            "Unsupported file type. Upload a PDF, TXT, or Markdown document.",
            "unsupported_file_type",
        )

    cleaned = text.strip()
    if not cleaned:
        raise bad_request("No readable text was found in the uploaded file.", "empty_parsed_text")

    safe_title = Path(filename).stem.replace("_", " ").replace("-", " ").strip()
    return SourceDocument(
        id=f"upload-{uuid4().hex[:10]}",
        title=(safe_title or "Uploaded Document")[:120],
        kind="uploaded",
        text=cleaned,
        metadata={
            "source": "uploaded-file",
            "filename": filename,
            "content_type": content_type or "unknown",
        },
    )


def _parse_text(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")


def _parse_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise bad_request("The PDF could not be read.", "invalid_pdf") from exc

    page_text: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text() or ""
        if extracted.strip():
            page_text.append(f"## Page {page_number}\n\n{extracted.strip()}")
    return "\n\n".join(page_text)

