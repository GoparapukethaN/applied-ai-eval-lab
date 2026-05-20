#!/usr/bin/env bash
set -euo pipefail

backend_port="${AIEL_VERIFY_BACKEND_PORT:-18001}"
frontend_port="${AIEL_VERIFY_FRONTEND_PORT:-13001}"
project="applied-ai-eval-lab-verify-${backend_port}-${frontend_port}-$$"

if command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
else
  python_cmd="python"
fi

export AIEL_BACKEND_PORT="$backend_port"
export AIEL_FRONTEND_PORT="$frontend_port"
export NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:${backend_port}"
export AIEL_FRONTEND_ORIGIN="http://127.0.0.1:${frontend_port}"

cleanup() {
  docker compose -p "$project" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker compose -p "$project" config --quiet
docker compose -p "$project" up --build -d

"$python_cmd" - <<PY
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

backend = "http://127.0.0.1:${backend_port}"
frontend = "http://127.0.0.1:${frontend_port}"


def request(method: str, url: str, payload: dict[str, object] | None = None):
    data = None if payload is None else json.dumps(payload).encode()
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status, response.headers, response.read()


def request_json(method: str, url: str, payload: dict[str, object] | None = None):
    status, _, body = request(method, url, payload)
    return status, json.loads(body.decode())


def wait_for_json(url: str, predicate, label: str):
    last_error = None
    for _ in range(120):
        try:
            status, payload = request_json("GET", url)
            if status == 200 and predicate(payload):
                return payload
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = exc
        time.sleep(1)
    raise AssertionError(f"{label} did not become ready: {last_error}")


def wait_for_text(url: str, expected: str, label: str):
    last_error = None
    for _ in range(120):
        try:
            status, _, body = request("GET", url)
            text = body.decode(errors="replace")
            if status == 200 and expected in text:
                return text
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
        time.sleep(1)
    raise AssertionError(f"{label} did not become ready: {last_error}")


health = wait_for_json(f"{backend}/health", lambda payload: payload["status"] == "ok", "backend")
assert health["service"] == "Applied AI Eval Lab", health

index_status, index_payload = request_json(
    "POST",
    f"{backend}/documents/index",
    {"document_ids": ["acme-ai-governance-policy"]},
)
assert index_status == 200
assert index_payload["document_count"] == 1, index_payload
assert index_payload["chunk_count"] > 0, index_payload

query_status, query = request_json(
    "POST",
    f"{backend}/query",
    {"question": "What should evaluation reports include?"},
)
assert query_status == 200
assert query["citations"], query
assert query["retrieved_chunks"], query
assert "answer quality" in query["answer"].lower(), query["answer"]

eval_status, evaluation = request_json("POST", f"{backend}/evaluation/run", {})
assert eval_status == 200
assert evaluation["example_count"] >= 4, evaluation
assert evaluation["gate"]["verdict"] in {"pass", "warn", "fail"}, evaluation

reports_status, reports = request_json("GET", f"{backend}/reports")
assert reports_status == 200
assert reports, reports

preflight = urllib.request.Request(
    f"{backend}/health",
    method="OPTIONS",
    headers={
        "Origin": frontend,
        "Access-Control-Request-Method": "GET",
    },
)
with urllib.request.urlopen(preflight, timeout=5) as response:
    assert response.status == 200
    assert response.headers["access-control-allow-origin"] == frontend

dashboard = wait_for_text(frontend, "Applied AI Eval Lab", "frontend")
assert "Run Eval" in dashboard
print("Applied AI Eval Lab Docker verification passed")
PY
