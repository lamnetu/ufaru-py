# app/main.py
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import health, rewrite
from app.config import settings
from app.core.exceptions import ServiceError
from app.core.logging import setup_logging

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    log.info("app.startup", environment=settings.environment)
    yield
    log.info("app.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Giga News Service",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # в проде — whitelist
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ServiceError)
    async def _service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(status_code=exc.status,
                            content={"code": exc.code, "message": exc.message})

    app.include_router(health.router)
    app.include_router(rewrite.router, prefix="/api/v1")

    if settings.environment != "test":
        Instrumentator().instrument(app).expose(app, include_in_schema=False)

    return app


app = create_app()
