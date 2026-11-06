"""Safe access to generated documents."""

import os
from pathlib import Path

from core.config import get_settings
from core.exceptions import DocumentNotFoundError


def get_document_path(name: str) -> Path:
    """Return the full path of a generated .docx, or raise DocumentNotFoundError."""
    safe_name = os.path.basename(name)  # blocks ../ path traversal
    path = get_settings().output_dir / safe_name
    if not safe_name.endswith(".docx") or not path.is_file():
        raise DocumentNotFoundError(safe_name)
    return path
