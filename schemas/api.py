"""Request and response models for the REST API."""

from pydantic import BaseModel, Field, field_validator

from schemas.document import Task


class AgentRequest(BaseModel):
    request: str = Field(min_length=10, max_length=2000, description="Plain-English request")

    @field_validator("request")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("request cannot be blank")
        return value.strip()


class AgentResponse(BaseModel):
    message: str
    doc_type: str
    plan_reasoning: str
    assumptions: list[str]
    task_list: list[Task]
    document: str
    download_url: str
