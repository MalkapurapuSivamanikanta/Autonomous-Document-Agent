"""The LangGraph workflow:

START -> plan -> execute --(more tasks?)--> execute
                    |
                    +--(all done)--> build -> END
"""

from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from agents.builder import build_node
from agents.executor import execute_node
from agents.planner import plan_node
from schemas.state import AgentState


def route_after_execute(state: AgentState) -> str:
    """The loop: keep executing until every task in the TODO list is done."""
    return "execute" if state["current"] < len(state["tasks"]) else "build"


@lru_cache
def get_graph():
    """Build and compile the graph once."""
    builder = StateGraph(AgentState)
    builder.add_node("plan", plan_node)
    builder.add_node("execute", execute_node)
    builder.add_node("build", build_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "execute")
    builder.add_conditional_edges("execute", route_after_execute, {"execute": "execute", "build": "build"})
    builder.add_edge("build", END)
    return builder.compile()
