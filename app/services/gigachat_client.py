# app/services/gigachat_client.py
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Protocol

import structlog
from gigachat import GigaChat
from gigachat.models import Chat, ChatCompletion, Messages, MessagesRole
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import settings
from app.core.exceptions import LLMContentFilteredError, LLMUnavailableError

log = structlog.get_logger()


@dataclass
class CompletionResult:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0
    finish_reason: str = ""


class LLMClient(Protocol):
    def complete(self, system: str, user: str, *,
                 temperature: float, max_tokens: int) -> CompletionResult: ...


@dataclass
class GigaChatClient:
    _client: GigaChat | None = field(default=None, init=False, repr=False)

    def _get(self) -> GigaChat:
        if self._client is None:
            self._client = GigaChat(
                credentials=settings.gigachat_credentials.get_secret_value(),
                scope=settings.gigachat_scope,
                model=settings.gigachat_model,
                base_url=settings.gigachat_base_url,
                verify_ssl_certs=settings.gigachat_verify_ssl_certs,
                timeout=settings.gigachat_timeout,
            )
            log.info("gigachat.client.initialized",
                     model=settings.gigachat_model, scope=settings.gigachat_scope)
        return self._client

    @retry(
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def complete(
        self,
        system: str,
        user: str,
        *,
        temperature: float,
        max_tokens: int,
    ) -> CompletionResult:
        t0 = time.perf_counter()
        try:
            payload = Chat(
                messages=[
                    Messages(role=MessagesRole.SYSTEM, content=system),
                    Messages(role=MessagesRole.USER, content=user),
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            resp: ChatCompletion = self._get().chat(payload)
        except Exception as exc:  # SDK кидает разные исключения — ловим всё
            log.warning("gigachat.call.failed", error=str(exc))
            raise LLMUnavailableError(str(exc)) from exc

        choice = resp.choices[0] if resp.choices else None
        if not choice or not choice.message or not choice.message.content:
            raise LLMUnavailableError("Empty response from LLM")

        content = choice.message.content.strip()
        usage = resp.usage

        # Модерация Сбера может фильтровать контент
        if choice.finish_reason == "content_filter":
            raise LLMContentFilteredError()

        duration_ms = int((time.perf_counter() - t0) * 1000)
        log.info(
            "gigachat.call.ok",
            duration_ms=duration_ms,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            finish_reason=choice.finish_reason,
        )

        return CompletionResult(
            content=content,
            model=resp.model or settings.gigachat_model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            duration_ms=duration_ms,
            finish_reason=choice.finish_reason or "",
        )

    def close(self) -> None:
        self._client = None
