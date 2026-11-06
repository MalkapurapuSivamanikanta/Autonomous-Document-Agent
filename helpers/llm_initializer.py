"""The single place where chat models are created."""

from langchain_openai import ChatOpenAI

from core.config import get_settings
from core.exceptions import LLMError


def get_llm(model_name: str | None = None) -> ChatOpenAI:
    """Create a ChatOpenAI client. Defaults to the primary model from settings."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise LLMError("OPENAI_API_KEY is not set. Add it to your .env file.")
    return ChatOpenAI(model=model_name or settings.primary_model, api_key=settings.openai_api_key)
