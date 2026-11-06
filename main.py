"""App entry point.  Run:  uvicorn main:app --reload   then open http://127.0.0.1:8000/docs"""

import logging

from fastapi import FastAPI

from api.routes import router
from core.config import get_settings
from core.logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    if not get_settings().openai_api_key:
        logging.getLogger(__name__).warning(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key, or /agent will return 502."
        )
    app = FastAPI(
        title="Autonomous Document Agent",
        description="POST /agent with a plain-English request. The agent plans its own TODO list, "
        "writes each section, and returns a Word document.",
    )
    app.include_router(router)
    return app


app = create_app()
