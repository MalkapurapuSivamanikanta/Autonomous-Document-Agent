"""The shared notebook that flows through the LangGraph workflow."""

import operator
from typing import Annotated

from typing_extensions import TypedDict


class AgentState(TypedDict):
    request: str  # the user's original request
    doc_type: str  # chosen by the planner
    title: str  # chosen by the planner
    reasoning: str  # why the planner chose this plan
    assumptions: list[str]  # assumptions the planner made
    tasks: list[dict]  # the agent-generated TODO list
    current: int  # index of the task being worked on
    sections: Annotated[list, operator.add]  # reducer: each new section is APPENDED
    doc_path: str  # file name of the finished .docx
