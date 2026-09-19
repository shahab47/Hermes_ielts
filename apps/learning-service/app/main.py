"""IELTS Learning Service entry point."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.diagnostic import router as diagnostic_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import ObservabilityMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Lifespan context manager for startup and shutdown events."""
    logger.info("learning_service_started", version="0.1.0")
    yield
    logger.info("learning_service_stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()

    app = FastAPI(
        title="IELTS Learning Service",
        version="0.1.0",
        description="Authoritative learning engine for IELTS Personal Learning Agent",
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(ObservabilityMiddleware)
    app.include_router(health_router)
    app.include_router(diagnostic_router)

    return app


app = create_app()
