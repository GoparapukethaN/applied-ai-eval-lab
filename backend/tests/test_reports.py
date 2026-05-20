from pathlib import Path

from app.evaluation.reports import list_reports, save_report
from app.evaluation.scoring import summarize_evaluation


def test_report_writer_saves_and_lists_report(tmp_path: Path) -> None:
    summary = summarize_evaluation([], [])
    summary.run_id = "eval-test"

    saved = save_report("evaluation", summary.run_id, summary, output_dir=tmp_path)
    reports = list_reports(output_dir=tmp_path)

    assert saved.filename.endswith("evaluation-eval-test.json")
    assert len(reports) == 1
    assert reports[0].run_id == "eval-test"
