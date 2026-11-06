"""Pure python-docx logic. No AI and no LangChain in this file."""

import uuid

from docx import Document
from docx.shared import Pt

from core.config import get_settings


def as_list(value) -> list[str]:
    """Models sometimes return a string, None or a mixed list. Always return a list of strings."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)] if str(value).strip() else []


def build_docx(title: str, doc_type: str, assumptions: list, tasks: list, sections: list, reasoning: str = "") -> str:
    """Build the Word file in the output folder and return its file name (not the full path)."""
    output_dir = get_settings().output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(11)

    doc.add_heading(str(title or "Untitled Document"), 0)
    doc.add_paragraph(f"Document type: {doc_type}")

    doc.add_heading("Assumptions", 1)
    for assumption in as_list(assumptions):
        doc.add_paragraph(assumption, style="List Bullet")

    for section in sections:
        doc.add_heading(str(section.get("heading") or "Section"), 1)
        for paragraph in as_list(section.get("paragraphs")):
            doc.add_paragraph(paragraph)
        for bullet in as_list(section.get("bullets")):
            doc.add_paragraph(bullet, style="List Bullet")

    doc.add_heading("Appendix: Agent Task List", 1)
    if str(reasoning).strip():
        doc.add_paragraph(f"Planning rationale: {reasoning}")
    for task in tasks:
        doc.add_paragraph(f"{task.get('id')}. {task.get('section')}: {task.get('goal')}", style="List Number")

    file_name = f"{uuid.uuid4().hex[:8]}.docx"
    doc.save(output_dir / file_name)
    return file_name
