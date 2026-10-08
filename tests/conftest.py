"""Fixtures condivise per la suite di test Pytest."""

import pytest
from fastapi.testclient import TestClient

from taskmaster.main import app


@pytest.fixture
def client() -> TestClient:
    """Fixture che restituisce un TestClient sincrono per invocare l'app FastAPI."""
    return TestClient(app)
