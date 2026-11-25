from fastapi import APIRouter

from app.api.schemas import RewriteRequest, RewriteResponse
from app.services.gigachat import gigachat_service

router = APIRouter()

SYSTEM_PROMPT = (
    "Ты — редактор городского новостного портала. "
    "Переработай текст новости: сделай его более читаемым, "
    "убери канцелярит, сохрани факты. Верни только готовый текст."
)


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_text(payload: RewriteRequest) -> RewriteResponse:
    rewritten = await gigachat_service.rewrite(payload.text, system_prompt=SYSTEM_PROMPT)
    return RewriteResponse(
        original=payload.text,
        rewritten=rewritten,
    )