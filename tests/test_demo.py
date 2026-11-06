"""run_demo.py must run both required inputs and save the evidence files."""

import json

from run_demo import main
from tests.conftest import failing


def test_demo_runs_both_inputs_and_saves_evidence(fake_llm, tmp_path):
    results = tmp_path / "results"
    assert main(results_dir=results) == 0
    for name in ("standard", "complex"):
        assert (results / f"{name}.docx").stat().st_size > 0
        body = json.loads((results / f"{name}_response.json").read_text())
        assert len(body["task_list"]) == 7 and body["plan_reasoning"]


def test_demo_reports_failure_when_llm_is_down(fake_llm, tmp_path):
    fake_llm.behavior = failing("down")
    fake_llm.json_behavior = failing("down")
    assert main(results_dir=tmp_path / "results") == 1
