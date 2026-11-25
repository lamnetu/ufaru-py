# app/core/cache.py
from __future__ import annotations

import hashlib
from typing import Any

from cachetools import TTLCache

from app.config import settings
from app.services.gigachat import CompletionResult


class InMemoryCache:
    def __init__(self) -> None:
        self._cache = TTLCache(
            maxsize=settings.cache_max_size, ttl=settings.cache_ttl_seconds
        )

    @staticmethod
    def _key(system: str, user: str, temperature: float, max_tokens: int) -> str:
        raw = f"{system}|{user}|{temperature}|{max_tokens}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(
        self, system: str, user: str, temperature: float, max_tokens: int
    ) -> CompletionResult | None:
        if not settings.cache_enabled:
            return None
        return self._cache.get(self._key(system, user, temperature, max_tokens))

    def set(
        self,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int,
        value: CompletionResult,
    ) -> None:
        if not settings.cache_enabled:
            return
        self._cache[self._key(system, user, temperature, max_tokens)] = value


cache = InMemoryCache()
