# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def app():
    import os
    os.environ.setdefault("GIGACHAT_CREDENTIALS", "test-creds")
    os.environ.setdefault("API_KEY", "test-key")
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("LOG_FORMAT", "console")
    return create_app()


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def auth_headers():
    return {"Authorization": "Bearer test-key"}
