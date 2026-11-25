from fastapi import APIRouter

from app.api.schemas import RewriteRequest, RewriteResponse

router = APIRouter()

@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(payload: RewriteRequest):
    return RewriteResponse(
        original=payload.text,
        rewritten=f"[GigaChat] {payload.text}",
    )