"""Test di fumo iniziale (Smoke Test) per verificare il corretto avvio dell'app."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_app_health_check(client: TestClient) -> None:
    """Verifica che l'endpoint di health check risponda con HTTP 200 e payload atteso."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "taskmaster-api"
