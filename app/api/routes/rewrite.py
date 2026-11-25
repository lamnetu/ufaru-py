from fastapi import APIRouter

from app.api.schemas import RewriteRequest, RewriteResponse
from app.services.gigachat import gigachat_service
from app.services.prompts import TEMPLATES
from app.core.enums import RewriteMode

router = APIRouter()


@router.get("/modes")
async def list_modes():
    """Список доступных режимов обработки."""
    return {
        mode.value: {
            "description": tpl.system[:100] + "...",
            "has_custom_prompt": mode == RewriteMode.CUSTOM,
        }
        for mode, tpl in TEMPLATES.items()
    }


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(payload: RewriteRequest) -> RewriteResponse:
    rewritten = await gigachat_service.rewrite(
        text=payload.text,
        mode=payload.mode,
        custom_prompt=payload.custom_prompt,
    )
    return RewriteResponse(
        original=payload.text,
        rewritten=rewritten,
        mode=payload.mode,
    )
