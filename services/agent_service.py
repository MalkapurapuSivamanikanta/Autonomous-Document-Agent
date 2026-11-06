"""Business logic: run the agent and shape the API response."""

import logging
from time import perf_counter

from core.config import get_settings
from graph.workflow import get_graph
from schemas.api import AgentResponse

logger = logging.getLogger(__name__)


def generate_document(request: str) -> AgentResponse:
    """Run plan -> execute (loop) -> build for one request."""
    started_at = perf_counter()
    logger.info("Document request received (length=%d characters)", len(request))
    result = get_graph().invoke(
        {"request": request, "sections": [], "current": 0},
        config={"recursion_limit": get_settings().recursion_limit},
    )
    response = AgentResponse(
        message=f"Created '{result['title']}' ({result['doc_type']}) with {len(result['sections'])} sections.",
        doc_type=result["doc_type"],
        plan_reasoning=result["reasoning"],
        assumptions=result["assumptions"],
        task_list=result["tasks"],
        document=result["doc_path"],
        download_url=f"/download/{result['doc_path']}",
    )
    logger.info(
        "Document request completed (title=%r, sections=%d, file=%s, elapsed=%.2fs)",
        result["title"],
        len(result["sections"]),
        result["doc_path"],
        perf_counter() - started_at,
    )
    return response
