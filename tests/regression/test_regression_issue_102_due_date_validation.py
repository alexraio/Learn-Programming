"""Test di regressione per Issue #102.

Bug segnalato:
I client potevano creare o aggiornare task specificando scadenze (due_date) nel passato,
corrompendo i report di sprint e il calcolo dei ritardi.
Regola di business: qualsiasi `due_date` specificata deve essere nel futuro rispetto al momento della richiesta.

Questo test verifica che una data nel passato venga rifiutata con HTTP 422.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient


@pytest.mark.regression
def test_regression_issue_102_cannot_create_task_with_past_due_date(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Verifica che la creazione di un task con scadenza nel passato venga bloccata (HTTP 422)."""
    proj = client.post("/api/v1/projects", json={"title": "Progetto SLA"}, headers=auth_headers)
    project_id = proj.json()["id"]

    past_date = (datetime.now(UTC) - timedelta(days=5)).isoformat()

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task con scadenza nel passato",
            "project_id": project_id,
            "due_date": past_date,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422, (
        f"Atteso HTTP 422 per scadenza nel passato, ricevuto {response.status_code}: {response.text}"
    )


@pytest.mark.regression
def test_regression_issue_102_allows_future_due_date(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Verifica che una data legittima nel futuro venga accettata normalmente (HTTP 201)."""
    proj = client.post("/api/v1/projects", json={"title": "Progetto Valido"}, headers=auth_headers)
    project_id = proj.json()["id"]

    future_date = (datetime.now(UTC) + timedelta(days=7)).isoformat()

    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Task con scadenza valida futura",
            "project_id": project_id,
            "due_date": future_date,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["due_date"] is not None
