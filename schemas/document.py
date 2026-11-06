"""Pydantic models the LLM must fill in (structured output)."""

from pydantic import BaseModel, Field


class Task(BaseModel):
    """One item in the agent's TODO list."""

    id: int
    section: str = Field(description="Section name, for example 'Risks'")
    goal: str = Field(description="What this section must achieve")


class Plan(BaseModel):
    """What the planner agent returns."""

    doc_type: str = Field(description="proposal, project plan, SOP, business report, etc.")
    title: str
    reasoning: str = Field(
        description="2 to 4 sentences: why this document type and structure, "
        "and how any conflicting requirements were resolved"
    )
    assumptions: list[str] = Field(description="Assumptions for missing information and resolved conflicts")
    tasks: list[Task] = Field(description="4 to 7 tasks, one per document section")


class Section(BaseModel):
    """What the executor agent returns for one task."""

    heading: str
    paragraphs: list[str]
    bullets: list[str]
