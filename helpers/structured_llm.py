"""The safe LLM call every agent uses: Pydantic validation + retry + fallback.

This is the project's mandatory engineering improvement (Retry and Fallback).

Attempt plan (default MAX_ATTEMPTS=3):
    attempts 1..n-1 : primary model, structured output (function/schema calling)
    last attempt    : fallback model, plain JSON mode parsed by Pydantic

The last attempt is a different *strategy* as well as (optionally) a different model, so the
fallback is meaningful even when PRIMARY_MODEL and FALLBACK_MODEL are the same model: if
structured output is what is failing, JSON mode still has a chance to work.
"""

import json
import logging
import time
from typing import TypeVar

from pydantic import BaseModel

from core.config import get_settings
from core.exceptions import LLMError
from helpers.llm_initializer import get_llm

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

STRUCTURED = "structured"
JSON_MODE = "json_mode"


def _call_structured(model_name: str, schema: type[T], system: str, user: str):
    """Strategy 1: ask the model to fill the Pydantic schema directly."""
    llm = get_llm(model_name).with_structured_output(schema)
    return llm.invoke([("system", system), ("user", user)])


def _call_json_mode(model_name: str, schema: type[T], system: str, user: str) -> T:
    """Strategy 2: JSON mode. Describe the schema in the prompt and parse the reply ourselves."""
    llm = get_llm(model_name).bind(response_format={"type": "json_object"})
    schema_hint = json.dumps(schema.model_json_schema())
    prompt = f"{system}\n\nReply with a single JSON object that matches this JSON schema exactly:\n{schema_hint}"
    reply = llm.invoke([("system", prompt), ("user", user)])
    return schema.model_validate_json(reply.content)


def ask(schema: type[T], system: str, user: str) -> T:
    """Call the LLM and return a validated `schema` object.

    Retries the primary model, then falls back (see module docstring). Every reply is validated
    by Pydantic, so a malformed answer counts as a failure and triggers the next attempt.
    Raises LLMError if every attempt fails.
    """
    settings = get_settings()
    attempts = [(settings.primary_model, STRUCTURED)] * (settings.max_attempts - 1)
    attempts.append((settings.fallback_model, JSON_MODE))
    last_error = "unknown"

    for number, (model_name, strategy) in enumerate(attempts, start=1):
        try:
            call = _call_structured if strategy == STRUCTURED else _call_json_mode
            result = call(model_name, schema, system, user)
            if result is None:
                raise ValueError("model returned no output")
            if not isinstance(result, schema):  # a dict -> validated Pydantic object
                result = schema.model_validate(result)
            return result
        except LLMError:
            raise  # configuration problem: retrying cannot help
        except Exception as error:
            last_error = f"{type(error).__name__}: {error}"
            logger.warning(
                "LLM attempt %d/%d (%s, %s) failed: %s", number, len(attempts), model_name, strategy, last_error[:200]
            )
            if number < len(attempts):
                time.sleep(settings.retry_delay)

    raise LLMError(f"All {len(attempts)} attempts failed. Last error: {last_error}")
