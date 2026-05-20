from pathlib import Path

import pytest

from app.evaluation.reports import list_reports, load_report, save_report
from app.evaluation.scoring import summarize_evaluation


def test_report_writer_saves_json_markdown_and_lists_report(tmp_path: Path) -> None:
    summary = summarize_evaluation([], [])
    summary.run_id = "eval-test"

    saved = save_report("evaluation", summary.run_id, summary, output_dir=tmp_path)
    reports = list_reports(output_dir=tmp_path)

    assert saved.filename.endswith("evaluation-eval-test.json")
    assert saved.markdown_filename.endswith("evaluation-eval-test.md")
    assert (tmp_path / saved.filename).exists()
    assert (tmp_path / saved.markdown_filename).exists()
    assert len(reports) == 1
    assert reports[0].run_id == "eval-test"
    assert reports[0].markdown_filename == saved.markdown_filename


def test_load_report_returns_saved_artifact(tmp_path: Path) -> None:
    summary = summarize_evaluation([], [])
    summary.run_id = "eval-test"
    saved = save_report("evaluation", summary.run_id, summary, output_dir=tmp_path)

    artifact = load_report(saved.filename, output_dir=tmp_path)

    assert artifact["kind"] == "evaluation"
    assert artifact["run_id"] == "eval-test"
    assert artifact["payload"]["gate"]["verdict"] == "fail"


def test_load_report_rejects_path_traversal(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_report("../outside.json", output_dir=tmp_path)
