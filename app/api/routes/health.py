# app/api/routes/health.py
from fastapi import APIRouter
from app.api.schemas import HealthResponse
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.service_name,
                          environment=settings.environment)


@router.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}
