"""Central settings. Everything tunable lives here and can be overridden from .env."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    primary_model: str  # used for the first (max_attempts - 1) tries
    fallback_model: str  # used for the last try
    max_attempts: int  # total LLM attempts per call
    retry_delay: float  # seconds to wait between failed attempts
    max_tasks: int  # guardrail: cap on the agent-generated TODO list
    recursion_limit: int  # LangGraph safety net against infinite loops
    output_dir: Path  # where generated .docx files are saved


@lru_cache
def get_settings() -> Settings:
    """Read settings from the environment once and cache them."""
    primary = os.getenv("PRIMARY_MODEL", "gpt-6-luna")
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        primary_model=primary,
        fallback_model=os.getenv("FALLBACK_MODEL", primary),
        max_attempts=int(os.getenv("MAX_ATTEMPTS", "3")),
        retry_delay=float(os.getenv("RETRY_DELAY", "1")),
        max_tasks=int(os.getenv("MAX_TASKS", "7")),
        recursion_limit=int(os.getenv("RECURSION_LIMIT", "50")),
        output_dir=Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "outputs")),
    )
