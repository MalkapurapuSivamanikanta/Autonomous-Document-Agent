"""Project-specific exceptions, so the API can map each one to the right HTTP status."""


class LLMError(Exception):
    """Every LLM attempt (retries plus the fallback model) failed, or the plan was unusable."""


class DocumentNotFoundError(Exception):
    """The requested .docx file does not exist or the name is not allowed."""
