# app/api/routes/rewrite.py
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_rewriter, verify_api_key
from app.api.schemas import RewriteRequest, RewriteResponse
from app.core.exceptions import (
    LLMContentFilteredError,
    LLMUnavailableError,
    ServiceError,
    TextTooLongError,
)
from app.services.rewriter import RewriteInput, Rewriter

router = APIRouter(prefix="/rewrite", tags=["rewrite"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=RewriteResponse, status_code=status.HTTP_200_OK)
async def rewrite(
    body: RewriteRequest,
    rewriter: Annotated[Rewriter, Depends(get_rewriter)],
) -> RewriteResponse:
    try:
        out = rewriter.rewrite(RewriteInput(
            text=body.text,
            mode=body.mode.value,
            custom_prompt=body.custom_prompt,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            target_audience=body.target_audience,
        ))
    except TextTooLongError as exc:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, exc.message) from exc
    except LLMContentFilteredError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.message) from exc
    except LLMUnavailableError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, exc.message) from exc
    except ServiceError as exc:
        raise HTTPException(exc.status, exc.message) from exc

#     publisher = get_publisher()
#     await publisher.publish(
#         settings.kafka_topic_out,
#         {"original": body.text, "result": out.result, "mode": body.mode.value,
#          "model": out.model, "tokens": out.total_tokens},
#         key=hashlib.sha256(body.text.encode()).hexdigest()[:16],
#     )

    return RewriteResponse(
        original=body.text,
        result=out.result,
        mode=body.mode,
        model=out.model,
        prompt_tokens=out.prompt_tokens,
        completion_tokens=out.completion_tokens,
        total_tokens=out.total_tokens,
        duration_ms=out.duration_ms,
        cached=out.cached,
    )

