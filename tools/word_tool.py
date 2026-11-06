"""LangChain tool wrapper around the Word builder."""

from langchain_core.tools import tool

from tools.docx_writer import build_docx


@tool
def create_word_document(
    title: str,
    doc_type: str,
    assumptions: list[str],
    tasks: list[dict],
    sections: list[dict],
    reasoning: str = "",
) -> str:
    """Create a polished Word (.docx) document from finished sections and return the file name."""
    return build_docx(title, doc_type, assumptions, tasks, sections, reasoning)
