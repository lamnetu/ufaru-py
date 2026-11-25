from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import ServiceError

# Импортируем из routes/ — как у тебя реально лежит
from app.api.routes.health import router as health_router
from app.api.routes.rewrite import router as rewrite_router


def create_app() -> FastAPI:
    app = FastAPI(title="GigaChat News Service", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ServiceError)
    async def _service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status,
            content={"code": exc.code, "message": exc.message},
        )

    app.include_router(health_router)
    app.include_router(rewrite_router, prefix="/api/v1")
    return app


app = create_app()