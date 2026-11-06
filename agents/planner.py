"""Planner agent: the LLM writes its own TODO list (the autonomous part)."""

import logging

from core.config import get_settings
from core.exceptions import LLMError
from helpers.structured_llm import ask
from schemas.document import Plan
from schemas.state import AgentState

logger = logging.getLogger(__name__)

PLANNER_PROMPT = (
    "You are a planning agent that creates professional business documents. "
    "Choose the most suitable document type (proposal, project plan, meeting minutes, "
    "business report, technical design, SOP, product specification, etc.). "
    "If information is missing, list a reasonable assumption for each gap. "
    "If requirements conflict, add an assumption explaining how you resolved the conflict. "
    "Create 4 to 7 tasks, one per document section, in a logical order. "
    "In `reasoning`, briefly explain why you chose this document type and structure."
)


def plan_node(state: AgentState) -> dict:
    """Decide the document type, title, assumptions and the TODO list."""
    logger.info("[plan] planning...")
    plan = ask(Plan, system=PLANNER_PROMPT, user=state["request"])

    # Code-level guardrails on top of Pydantic validation.
    tasks = [task.model_dump() for task in plan.tasks][: get_settings().max_tasks]
    if not tasks:
        raise LLMError("Planner returned no tasks")
    for number, task in enumerate(tasks, start=1):  # renumber ids cleanly
        task["id"] = number

    logger.info(
        "[plan] completed: title=%r, type=%s, tasks=%d, assumptions=%d",
        plan.title,
        plan.doc_type,
        len(tasks),
        len(plan.assumptions),
    )
    for task in tasks:
        logger.info("[plan] task %d: %s", task["id"], task["section"])
    return {
        "doc_type": plan.doc_type,
        "title": plan.title,
        "reasoning": plan.reasoning,
        "assumptions": plan.assumptions,
        "tasks": tasks,
        "current": 0,
    }
