# tests/test_api.py
from unittest.mock import MagicMock

import pytest

from app.services.gigachat_client import CompletionResult


def _ok_result(content="Переработанный текст."):
    return CompletionResult(
        content=content, model="GigaChat-Plus",
        prompt_tokens=100, completion_tokens=50,
        total_tokens=150, duration_ms=420,
    )


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_rewrite_unauthorized(client):
    r = client.post("/api/v1/rewrite", json={"text": "x" * 20})
    assert r.status_code == 403


def test_rewrite_ok(client, auth_headers, monkeypatch):
    from app.api import deps
    fake_llm = MagicMock()
    fake_llm.complete.return_value = _ok_result()
    deps._gigachat = None
    deps._rewriter = None
    monkeypatch.setattr(deps, "get_gigachat", lambda: fake_llm)

    r = client.post("/api/v1/rewrite", headers=auth_headers, json={
        "text": "В городе N открыли новый парк площадью 5 гектаров.",
        "mode": "rewrite",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["result"] == "Переработанный текст."
    assert body["mode"] == "rewrite"
    assert body["total_tokens"] == 150


def test_rewrite_text_too_long(client, auth_headers):
    r = client.post("/api/v1/rewrite", headers=auth_headers, json={
        "text": "a" * 25_000,
    })
    assert r.status_code == 413


def test_rewrite_invalid_mode(client, auth_headers):
    r = client.post("/api/v1/rewrite", headers=auth_headers, json={
        "text": "x" * 20, "mode": "nonsense",
    })
    assert r.status_code == 422
