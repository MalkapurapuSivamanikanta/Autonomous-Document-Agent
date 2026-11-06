"""Builder agent: turns the finished sections into the Word document using a tool."""

import logging

from core.config import get_settings
from schemas.state import AgentState
from tools.word_tool import create_word_document

logger = logging.getLogger(__name__)


def build_node(state: AgentState) -> dict:
    """Hand the finished sections to the Word tool. No LLM is involved in this step."""
    logger.info("[build] creating the Word document...")
    file_name = create_word_document.invoke(
        {
            "title": state["title"],
            "doc_type": state["doc_type"],
            "reasoning": state.get("reasoning", ""),
            "assumptions": state["assumptions"],
            "tasks": state["tasks"],
            "sections": state["sections"],
        }
    )
    document_path = (get_settings().output_dir / file_name).resolve()
    logger.info(
        "[build] Word document created successfully: %s (%d bytes)",
        document_path,
        document_path.stat().st_size,
    )
    return {"doc_path": file_name}
