"""Full graph run with a fake LLM."""

import pytest

from core.exceptions import LLMError
from graph.workflow import route_after_execute
from services.agent_service import generate_document


def test_full_run_loops_once_per_task_and_builds_file(fake_llm, tmp_path):
    response = generate_document("Create a project plan for a mobile app launch.")

    assert fake_llm.count("Plan") == 1
    assert fake_llm.count("Section") == 7  # plan had 9 tasks, capped at 7
    assert len(response.task_list) == 7
    assert [t.id for t in response.task_list] == list(range(1, 8))
    assert (tmp_path / response.document).exists()
    assert response.download_url == f"/download/{response.document}"
    assert response.assumptions == ["Assumed budget"]
    assert response.plan_reasoning == "A project plan fits a launch request."


def test_short_plan_runs_exactly_that_many_sections(fake_llm):
    fake_llm.plan_tasks = 4
    response = generate_document("Create a short SOP for onboarding.")
    assert fake_llm.count("Section") == 4
    assert "4 sections" in response.message


def test_empty_plan_is_rejected(fake_llm):
    fake_llm.plan_tasks = 0
    with pytest.raises(LLMError):
        generate_document("Create something with no tasks at all.")


def test_router_loops_then_builds():
    assert route_after_execute({"current": 1, "tasks": [1, 2, 3]}) == "execute"
    assert route_after_execute({"current": 3, "tasks": [1, 2, 3]}) == "build"
