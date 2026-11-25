import base64
import time
import uuid
from typing import Optional

import httpx
from loguru import logger

from app.core.config import settings
from app.core.exceptions import ServiceError


class GigaChatService:
    def __init__(self) -> None:
        self._token: Optional[str] = None
        self._token_expires_at: float = 0

        verify = settings.gigachat_verify_ssl

        # Клиент для OAuth (отдельный хост)
        self._oauth_client = httpx.AsyncClient(
            timeout=30.0,
            verify=verify,
        )

        # Клиент для Chat API
        self._api_client = httpx.AsyncClient(
            base_url=settings.gigachat_api_url,
            timeout=60.0,  # генерация может быть долгой
            verify=verify,
        )

    async def _get_token(self, force_refresh: bool = False) -> str:
        now = time.time()
        if not force_refresh and self._token and now < self._token_expires_at - 60:
            return self._token

        logger.info("GigaChat: requesting new OAuth token")

        credentials = base64.b64encode(settings.gigachat_api_key.encode()).decode()
        rq_uid = str(uuid.uuid4())

        try:
            resp = await self._oauth_client.post(
                settings.gigachat_oauth_url,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "RqUID": rq_uid,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                data={"scope": settings.gigachat_scope},
            )
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"GigaChat OAuth HTTP error: {e.response.status_code} {e.response.text}")
            raise ServiceError(
                status=502,
                code="gigachat_auth_failed",
                message=f"OAuth ошибка: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            logger.error(f"GigaChat OAuth connection error: {type(e).__name__} — {e}")
            raise ServiceError(
                status=503,
                code="gigachat_unavailable",
                message=f"Не удалось соединиться с OAuth: {type(e).__name__}",
            )

        self._token = data["tok"]  # GigaChat возвращает поле "tok", не "access_token"!
        self._token_expires_at = now + data.get("expires_at", 1800)  # fallback 30 мин
        logger.info(f"GigaChat: token received, valid for ~{data.get('expires_at', 1800)}s")
        return self._token

    async def rewrite(self, text: str, system_prompt: Optional[str] = None) -> str:
        token = await self._get_token()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": text})

        payload = {
            "model": "GigaChat",
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1500,
        }

        try:
            resp = await self._api_client.post(
                "/chat/completions",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if resp.status_code == 401:
                logger.warning("GigaChat: 401, refreshing token and retrying")
                token = await self._get_token(force_refresh=True)
                resp = await self._api_client.post(
                    "/chat/completions",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )

            resp.raise_for_status()
            data = resp.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"GigaChat API HTTP error: {e.response.status_code} {e.response.text}")
            raise ServiceError(
                status=502,
                code="gigachat_completion_failed",
                message=f"Ошибка генерации: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            logger.error(f"GigaChat API connection error: {type(e).__name__} — {e}")
            raise ServiceError(
                status=503,
                code="gigachat_unavailable",
                message=f"Не удалось соединиться с API: {type(e).__name__}",
            )

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            logger.error(f"GigaChat unexpected response: {data}")
            raise ServiceError(
                status=502,
                code="gigachat_bad_response",
                message="Неожиданный формат ответа",
            )

    async def close(self) -> None:
        await self._oauth_client.aclose()
        await self._api_client.aclose()


gigachat_service = GigaChatService()