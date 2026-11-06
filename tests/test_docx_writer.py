from docx import Document

from tools.docx_writer import as_list, build_docx
from tools.word_tool import create_word_document


def test_as_list_handles_messy_values():
    assert as_list(None) == []
    assert as_list("one string") == ["one string"]
    assert as_list(["a", "", "b"]) == ["a", "b"]
    assert as_list(42) == ["42"]


def test_build_docx_creates_file_with_expected_headings(tmp_path):
    name = build_docx(
        title="My Doc",
        doc_type="proposal",
        assumptions=["A1"],
        tasks=[{"id": 1, "section": "Intro", "goal": "Say hello"}],
        sections=[{"heading": "Intro", "paragraphs": ["Hello."], "bullets": ["x"]}],
    )
    assert name.endswith(".docx")
    doc = Document(tmp_path / name)
    headings = [p.text for p in doc.paragraphs if p.style.name.startswith(("Heading", "Title"))]
    assert headings == ["My Doc", "Assumptions", "Intro", "Appendix: Agent Task List"]


def test_planning_rationale_is_written_into_the_appendix(tmp_path):
    name = build_docx("T", "d", [], [{"id": 1, "section": "A", "goal": "g"}], [], reasoning="Because it fits.")
    texts = [p.text for p in Document(tmp_path / name).paragraphs]
    assert "Planning rationale: Because it fits." in texts


def test_build_docx_survives_messy_sections(tmp_path):
    name = build_docx(
        title="",
        doc_type="x",
        assumptions="single string",
        tasks=[],
        sections=[{"paragraphs": "a string, not a list", "bullets": None}],  # no heading
    )
    doc = Document(tmp_path / name)
    texts = [p.text for p in doc.paragraphs]
    assert "Section" in texts and "a string, not a list" in texts and "Untitled Document" in texts


def test_word_tool_is_a_langchain_tool(tmp_path):
    assert create_word_document.name == "create_word_document"
    name = create_word_document.invoke({"title": "T", "doc_type": "d", "assumptions": [], "tasks": [], "sections": []})
    assert (tmp_path / name).exists()
