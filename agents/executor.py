"""Executor agent: writes ONE section per visit. The graph loops it until the TODO list is done."""

import logging

from helpers.structured_llm import ask
from schemas.document import Section
from schemas.state import AgentState

logger = logging.getLogger(__name__)

EXECUTOR_PROMPT = (
    "You write one section of a professional business document. "
    "Use realistic mock data where needed. Do not repeat content from earlier sections. "
    "Write 2 to 4 paragraphs and 3 to 6 bullets."
)


def execute_node(state: AgentState) -> dict:
    """Write the section for tasks[current], then move the counter on."""
    index = state["current"]
    task = state["tasks"][index]
    logger.info("[execute] task %d/%d: %s", index + 1, len(state["tasks"]), task["section"])

    already_written = [section.get("heading", "") for section in state["sections"]]
    section = ask(
        Section,
        system=EXECUTOR_PROMPT,
        user=(
            f"Original request: {state['request']}\n"
            f"Document: {state['title']} ({state['doc_type']})\n"
            f"Assumptions: {state['assumptions']}\n"
            f"Sections already written: {already_written}\n"
            f"Write this section now: {task}"
        ),
    )
    logger.info(
        "[execute] completed task %d/%d: %s (paragraphs=%d, bullets=%d)",
        index + 1,
        len(state["tasks"]),
        section.heading,
        len(section.paragraphs),
        len(section.bullets),
    )
    # Return only the NEW section; the reducer on AgentState.sections appends it.
    return {"sections": [section.model_dump()], "current": index + 1}
