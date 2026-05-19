from pathlib import Path

from app.evaluation.reports import list_reports, save_report
from app.models.schemas import EvaluationSummary


def test_report_writer_saves_and_lists_report(tmp_path: Path) -> None:
    summary = EvaluationSummary(
        run_id="eval-test",
        example_count=0,
        retrieval_hit_rate=0,
        average_citation_coverage=0,
        average_latency_ms=0,
        estimated_total_cost_usd=0,
        failure_count=0,
        items=[],
    )

    saved = save_report("evaluation", summary.run_id, summary, output_dir=tmp_path)
    reports = list_reports(output_dir=tmp_path)

    assert saved.filename.endswith("evaluation-eval-test.json")
    assert len(reports) == 1
    assert reports[0].run_id == "eval-test"

