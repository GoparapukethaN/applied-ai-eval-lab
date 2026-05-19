from fastapi.testclient import TestClient

from app.documents.parsing import parse_uploaded_document
from app.main import app


client = TestClient(app)


def test_parse_uploaded_text_document() -> None:
    document = parse_uploaded_document(
        filename="security-policy.txt",
        content_type="text/plain",
        content=b"# Policy\n\n## Security\n\nSecrets stay private.",
    )

    assert document.kind == "uploaded"
    assert document.title == "security policy"
    assert "Secrets stay private" in document.text


def test_upload_document_indexes_chunks() -> None:
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "policy.txt",
                b"# Policy\n\n## Security\n\nSecrets must stay in managed storage.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_count"] == 1
    assert payload["chunk_count"] >= 1


def test_experiment_run_compares_retrieval_configs() -> None:
    client.post("/documents/index", json={"document_ids": ["acme-ai-governance-policy"]})
    response = client.post("/experiments/run", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["winner"] in {"focused", "balanced", "broad"}
    assert len(payload["results"]) == 3
    assert all("summary" in result for result in payload["results"])

