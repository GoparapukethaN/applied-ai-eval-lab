from app.documents.chunking import chunk_document, normalize_text, split_sections
from app.models.schemas import SourceDocument


def test_normalize_text_removes_extra_spacing() -> None:
    text = "Alpha   beta\n\n\nGamma\t delta"
    assert normalize_text(text) == "Alpha beta\n\nGamma delta"


def test_split_sections_extracts_markdown_headings() -> None:
    sections = split_sections("# Policy\n\nIntro\n\n## Security\n\nEncrypt data")
    assert [section.title for section in sections] == ["Policy", "Security"]
    assert sections[1].text == "Encrypt data"


def test_chunk_document_preserves_source_metadata() -> None:
    document = SourceDocument(
        id="doc-1",
        title="Policy",
        text="# Policy\n\n## Security\n\nEncrypt data at rest and in transit.",
    )
    chunks = chunk_document(document, chunk_size=10, chunk_overlap=2)
    assert len(chunks) == 1
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].document_title == "Policy"
    assert chunks[0].section == "Security"
    assert "Encrypt data" in chunks[0].text
    assert chunks[0].token_count > 0

