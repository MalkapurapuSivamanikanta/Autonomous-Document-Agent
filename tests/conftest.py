"""Shared test setup: a fake LLM so no API key or network is needed."""

import pytest

from core.config import get_settings
from graph.workflow import get_graph
from schemas.document import Plan, Section


def failing(message: str = "boom"):
    """Return a fake behavior that always raises, for simulating an LLM outage."""

    def behavior(*args, **kwargs):
        raise RuntimeError(message)

    return behavior


class FakeStructured:
    """Stands in for llm.with_structured_output(schema)."""

    def __init__(self, controller, model, schema):
        self.controller, self.model, self.schema = controller, model, schema

    def invoke(self, messages):
        self.controller.calls.append((self.model, self.schema.__name__))
        return self.controller.behavior(self.model, self.schema)


class FakeBound:
    """Stands in for llm.bind(response_format=json_object): returns raw text in .content."""

    def __init__(self, controller, model):
        self.controller, self.model = controller, model

    def invoke(self, messages):
        self.controller.calls.append((self.model, "json_mode"))
        self.controller.json_messages = messages
        return type("Reply", (), {"content": self.controller.json_behavior(self.model)})()


class FakeLLM:
    def __init__(self, controller, model):
        self.controller, self.model = controller, model

    def with_structured_output(self, schema):
        return FakeStructured(self.controller, self.model, schema)

    def bind(self, **kwargs):
        return FakeBound(self.controller, self.model)


class FakeController:
    """Records every call and decides what the fake model returns (or raises)."""

    def __init__(self, plan_tasks: int = 9):
        self.calls: list[tuple[str, str]] = []
        self.plan_tasks = plan_tasks
        self.json_messages = None
        self.behavior = self.default_behavior
        self.json_behavior = self.default_json_behavior

    def default_behavior(self, model, schema):
        if schema is Plan:
            tasks = [{"id": 99, "section": f"Section {i}", "goal": "goal"} for i in range(self.plan_tasks)]
            return Plan(
                doc_type="project plan",
                title="Test Plan",
                reasoning="A project plan fits a launch request.",
                assumptions=["Assumed budget"],
                tasks=tasks,
            )
        if schema is Section:
            return Section(heading="Heading", paragraphs=["A paragraph."], bullets=["A bullet"])
        raise AssertionError(f"unexpected schema {schema}")

    def default_json_behavior(self, model):
        raise AssertionError("JSON mode was not expected in this test")

    def count(self, schema_name: str) -> int:
        return sum(1 for _, name in self.calls if name == schema_name)


@pytest.fixture(autouse=True)
def test_settings(monkeypatch, tmp_path):
    """Fixed model names, no waiting between retries, and a temp output folder."""
    monkeypatch.setenv("PRIMARY_MODEL", "primary-x")
    monkeypatch.setenv("FALLBACK_MODEL", "fallback-x")
    monkeypatch.setenv("RETRY_DELAY", "0")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))
    get_settings.cache_clear()
    get_graph.cache_clear()
    yield
    get_settings.cache_clear()
    get_graph.cache_clear()


@pytest.fixture
def fake_llm(monkeypatch):
    controller = FakeController()
    monkeypatch.setattr("helpers.structured_llm.get_llm", lambda model=None: FakeLLM(controller, model))
    return controller
