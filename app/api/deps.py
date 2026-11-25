# app/api/deps.py
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.services.gigachat import GigaChatClient
from app.services.rewriter import Rewriter

_bearer = HTTPBearer()

_gigachat: GigaChatClient | None = None
_rewriter: Rewriter | None = None


def get_gigachat() -> GigaChatClient:
    global _gigachat
    if _gigachat is None:
        _gigachat = GigaChatClient()
    return _gigachat


def get_rewriter(llm: Annotated[GigaChatClient, Depends(get_gigachat)]) -> Rewriter:
    global _rewriter
    if _rewriter is None:
        _rewriter = Rewriter(llm, max_text_chars=settings.max_request_text_chars)
    return _rewriter


async def verify_api_key(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> None:
    if creds.credentials != settings.api_key.get_secret_value():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")
