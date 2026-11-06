"""Retry and fallback: the mandatory engineering improvement."""

import pytest
from pydantic import BaseModel

from core.config import get_settings
from core.exceptions import LLMError
from helpers.llm_initializer import get_llm
from helpers.structured_llm import ask
from tests.conftest import failing


class Ping(BaseModel):
    ok: bool


def test_success_on_first_try(fake_llm):
    fake_llm.behavior = lambda model, schema: Ping(ok=True)
    assert ask(Ping, "sys", "user").ok is True
    assert fake_llm.calls == [("primary-x", "Ping")]


def test_retries_primary_then_succeeds(fake_llm):
    attempts = {"n": 0}

    def flaky(model, schema):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise RuntimeError("rate limited")
        return Ping(ok=True)

    fake_llm.behavior = flaky
    assert ask(Ping, "sys", "user").ok is True
    assert fake_llm.calls == [("primary-x", "Ping"), ("primary-x", "Ping")]


def test_last_attempt_falls_back_to_fallback_model_in_json_mode(fake_llm):
    fake_llm.behavior = failing("structured output unsupported")
    fake_llm.json_behavior = lambda model: '{"ok": true}'
    assert ask(Ping, "sys", "user").ok is True
    assert fake_llm.calls == [("primary-x", "Ping"), ("primary-x", "Ping"), ("fallback-x", "json_mode")]


def test_json_mode_prompt_contains_word_json_and_the_schema(fake_llm):
    fake_llm.behavior = failing("down")
    fake_llm.json_behavior = lambda model: '{"ok": true}'
    ask(Ping, "You are helpful.", "user text")
    system_prompt = fake_llm.json_messages[0][1]
    assert "JSON" in system_prompt and '"ok"' in system_prompt  # OpenAI JSON mode requires the word JSON


def test_raises_llm_error_when_everything_fails(fake_llm):
    fake_llm.behavior = failing()
    fake_llm.json_behavior = failing()
    with pytest.raises(LLMError):
        ask(Ping, "sys", "user")
    assert len(fake_llm.calls) == 3


def test_invalid_structured_reply_is_retried(fake_llm):
    replies = iter([{"wrong": "shape"}, Ping(ok=True)])  # first reply breaks the schema
    fake_llm.behavior = lambda model, schema: next(replies)
    assert ask(Ping, "sys", "user").ok is True
    assert len(fake_llm.calls) == 2


def test_malformed_json_in_fallback_is_a_failure(fake_llm):
    fake_llm.behavior = failing("down")
    fake_llm.json_behavior = lambda model: "this is not json"
    with pytest.raises(LLMError):
        ask(Ping, "sys", "user")


def test_missing_api_key_fails_fast_without_retries(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(LLMError, match="OPENAI_API_KEY"):
        get_llm()
    sleeps = []
    monkeypatch.setattr("helpers.structured_llm.time.sleep", lambda s: sleeps.append(s))
    with pytest.raises(LLMError, match="OPENAI_API_KEY"):
        ask(Ping, "sys", "user")
    assert sleeps == []  # no pointless retries on a configuration error
