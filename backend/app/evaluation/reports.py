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
    filename = f"{created_at.strftime('%Y%m%dT%H%M%SZ')}-{kind}-{run_id}.json"
    path = reports_dir / filename
    serialized: dict[str, Any] = {
        "kind": kind,
        "run_id": run_id,
        "created_at": created_at.isoformat(),
        "payload": payload.model_dump(mode="json"),
    }
    path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
    return ReportSummary(
        kind=kind,
        run_id=run_id,
        filename=filename,
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
                    created_at=datetime.fromisoformat(data["created_at"]),
                )
            )
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
    return reports

