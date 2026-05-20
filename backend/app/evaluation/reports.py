from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.models.schemas import ReportSummary


def save_report(
    kind: str,
    run_id: str,
    payload: BaseModel,
    output_dir: Path | None = None,
) -> ReportSummary:
    reports_dir = output_dir or Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc)
    filename_base = f"{created_at.strftime('%Y%m%dT%H%M%SZ')}-{kind}-{run_id}"
    filename = f"{filename_base}.json"
    markdown_filename = f"{filename_base}.md"
    json_path = reports_dir / filename
    markdown_path = reports_dir / markdown_filename
    serialized: dict[str, Any] = {
        "kind": kind,
        "run_id": run_id,
        "created_at": created_at.isoformat(),
        "payload": payload.model_dump(mode="json"),
    }
    json_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
    markdown_path.write_text(
        render_report_markdown(kind, run_id, serialized["payload"]),
        encoding="utf-8",
    )
    return ReportSummary(
        kind=kind,
        run_id=run_id,
        filename=filename,
        markdown_filename=markdown_filename,
        created_at=created_at,
    )


def list_reports(output_dir: Path | None = None) -> list[ReportSummary]:
    reports_dir = output_dir or Path("artifacts/reports")
    if not reports_dir.exists():
        return []

    reports: list[ReportSummary] = []
    for path in sorted(reports_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            reports.append(
                ReportSummary(
                    kind=data["kind"],
                    run_id=data["run_id"],
                    filename=path.name,
                    markdown_filename=_markdown_name(path),
                    created_at=datetime.fromisoformat(data["created_at"]),
                )
            )
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
    return reports


def load_report(filename: str, output_dir: Path | None = None) -> dict[str, Any]:
    path = _safe_report_path(filename, output_dir=output_dir, suffix=".json")
    if not path.exists():
        raise FileNotFoundError(filename)
    return json.loads(path.read_text(encoding="utf-8"))


def load_report_markdown(filename: str, output_dir: Path | None = None) -> str:
    markdown_filename = filename if filename.endswith(".md") else filename.removesuffix(".json") + ".md"
    path = _safe_report_path(markdown_filename, output_dir=output_dir, suffix=".md")
    if not path.exists():
        raise FileNotFoundError(markdown_filename)
    return path.read_text(encoding="utf-8")


def render_report_markdown(kind: str, run_id: str, payload: dict[str, Any]) -> str:
    if kind == "evaluation":
        return _render_evaluation_markdown(run_id, payload)
    if kind == "experiment":
        return _render_experiment_markdown(run_id, payload)
    return "\n".join([
        f"# {kind.title()} Report",
        "",
        f"- Run ID: `{run_id}`",
        "",
        "```json",
        json.dumps(payload, indent=2),
        "```",
        "",
    ])


def _render_evaluation_markdown(run_id: str, payload: dict[str, Any]) -> str:
    gate = payload.get("gate", {})
    lines = [
        "# Evaluation Report",
        "",
        f"- Run ID: `{run_id}`",
        f"- Gate verdict: `{gate.get('verdict', 'unknown')}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Examples | {payload.get('example_count', 0)} |",
        f"| Retrieval hit rate | {payload.get('retrieval_hit_rate', 0)} |",
        f"| Citation coverage | {payload.get('average_citation_coverage', 0)} |",
        f"| Average latency | {payload.get('average_latency_ms', 0)} ms |",
        f"| Failure count | {payload.get('failure_count', 0)} |",
        "",
        "## Gate Checks",
        "",
        "| Check | Passed | Observed | Threshold | Severity |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for check in gate.get("checks", []):
        lines.append(
            "| {name} | {passed} | {observed} | {threshold} | {severity} |".format(
                name=check.get("name", "unknown"),
                passed=str(check.get("passed", False)).lower(),
                observed=check.get("observed", "n/a"),
                threshold=check.get("threshold", "n/a"),
                severity=check.get("severity", "n/a"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_experiment_markdown(run_id: str, payload: dict[str, Any]) -> str:
    lines = [
        "# Experiment Report",
        "",
        f"- Run ID: `{run_id}`",
        f"- Winner: `{payload.get('winner', 'unknown')}`",
        "",
        "## Results",
        "",
        "| Config | Top K | Verdict | Hit Rate | Citation Coverage | Latency | Failures |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for result in payload.get("results", []):
        config = result.get("config", {})
        summary = result.get("summary", {})
        gate = summary.get("gate", {})
        lines.append(
            "| {config_id} | {top_k} | {verdict} | {hit_rate} | {coverage} | {latency} ms | {failures} |".format(
                config_id=config.get("id", "unknown"),
                top_k=config.get("top_k", "n/a"),
                verdict=gate.get("verdict", "unknown"),
                hit_rate=summary.get("retrieval_hit_rate", "n/a"),
                coverage=summary.get("average_citation_coverage", "n/a"),
                latency=summary.get("average_latency_ms", "n/a"),
                failures=summary.get("failure_count", "n/a"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _markdown_name(json_path: Path) -> str | None:
    markdown_path = json_path.with_suffix(".md")
    return markdown_path.name if markdown_path.exists() else None


def _safe_report_path(
    filename: str,
    *,
    output_dir: Path | None,
    suffix: str,
) -> Path:
    if Path(filename).name != filename or not filename.endswith(suffix):
        raise FileNotFoundError(filename)
    reports_dir = output_dir or Path("artifacts/reports")
    return reports_dir / filename
