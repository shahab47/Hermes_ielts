"""IELTS Learning Service entry point."""
from __future__ import annotations

import structlog
from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging

logger = structlog.get_logger()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    app = FastAPI(
        title="IELTS Learning Service",
        version="0.1.0",
        description="Authoritative learning engine for IELTS Personal Learning Agent",
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )

    app.include_router(health_router)

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("learning_service_started", version="0.1.0")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("learning_service_stopped")

    return app


app = create_app()
