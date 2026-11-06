"""REST endpoints. Thin on purpose: validation here, logic in services/."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from core.exceptions import DocumentNotFoundError, LLMError
from schemas.api import AgentRequest, AgentResponse
from services import agent_service, document_service

logger = logging.getLogger(__name__)
router = APIRouter()

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/agent", response_model=AgentResponse)
def create_document(body: AgentRequest) -> AgentResponse:
    """Plan, write and build a Word document from a plain-English request."""
    try:
        return agent_service.generate_document(body.request)
    except LLMError as error:
        logger.error("LLM failure: %s", error)
        raise HTTPException(status_code=502, detail=f"LLM failed after retries and fallback: {error}") from error
    except Exception as error:
        logger.exception("Unexpected agent error")
        raise HTTPException(status_code=500, detail=f"Agent error: {error}") from error


@router.get("/download/{name}")
def download(name: str) -> FileResponse:
    """Download a generated .docx by file name."""
    try:
        path = document_service.get_document_path(name)
    except DocumentNotFoundError:
        logger.warning("Document download not found: %s", name)
        raise HTTPException(status_code=404, detail="File not found") from None
    logger.info("Document download requested: %s", path)
    return FileResponse(path, filename=path.name, media_type=DOCX_MEDIA_TYPE)
