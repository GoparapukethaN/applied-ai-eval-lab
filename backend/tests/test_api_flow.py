from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ingest_to_query_flow_returns_citations() -> None:
    index_response = client.post(
        "/documents/index",
        json={"document_ids": ["acme-ai-governance-policy"]},
    )
    assert index_response.status_code == 200
    assert index_response.json()["chunk_count"] > 0

    query_response = client.post(
        "/query",
        json={"question": "What should evaluation reports include?"},
    )
    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["citations"]
    assert payload["retrieved_chunks"]
    assert "answer quality" in payload["answer"].lower()


def test_evaluation_run_returns_summary() -> None:
    response = client.post("/evaluation/run", json={})
    assert response.status_code == 200
    payload = response.json()
    assert payload["example_count"] >= 4
    assert "retrieval_hit_rate" in payload

