# app/services/rewriter.py
from __future__ import annotations

from dataclasses import dataclass

import structlog

from app.core.cache import cache
from app.core.exceptions import TextTooLongError
from app.services.gigachat import CompletionResult, LLMClient
from app.services.prompts import build_messages

log = structlog.get_logger()


@dataclass
class RewriteInput:
    text: str
    mode: str
    custom_prompt: str | None
    temperature: float
    max_tokens: int
    target_audience: str | None


@dataclass
class RewriteOutput:
    result: str
    mode: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_ms: int
    cached: bool = False


class Rewriter:
    def __init__(self, llm: LLMClient, *, max_text_chars: int):
        self._llm = llm
        self._max_text_chars = max_text_chars

    def rewrite(self, inp: RewriteInput) -> RewriteOutput:
        if len(inp.text) > self._max_text_chars:
            raise TextTooLongError(self._max_text_chars, len(inp.text))

        text = inp.text.strip()
        if inp.target_audience:
            text = f"[Целевая аудитория: {inp.target_audience}]\n\n{text}"

        system, user = build_messages(inp.mode, text, inp.custom_prompt)

        if (
            cached := cache.get(system, user, inp.temperature, inp.max_tokens)
        ) is not None:
            log.info("rewriter.cache.hit", mode=inp.mode)
            return RewriteOutput(
                result=cached.content,
                mode=inp.mode,
                model=cached.model,
                prompt_tokens=cached.prompt_tokens,
                completion_tokens=cached.completion_tokens,
                total_tokens=cached.total_tokens,
                duration_ms=cached.duration_ms,
                cached=True,
            )

        result: CompletionResult = self._llm.complete(
            system, user, temperature=inp.temperature, max_tokens=inp.max_tokens
        )
        cache.set(system, user, inp.temperature, inp.max_tokens, result)

        log.info(
            "rewriter.ok",
            mode=inp.mode,
            duration_ms=result.duration_ms,
            tokens=result.total_tokens,
            cached=False,
        )

        return RewriteOutput(
            result=result.content,
            mode=inp.mode,
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.total_tokens,
            duration_ms=result.duration_ms,
            cached=False,
        )
