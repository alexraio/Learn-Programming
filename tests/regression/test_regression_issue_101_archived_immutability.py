"""Test di regressione per Issue #101.

Bug segnalato:
Gli utenti erano in grado di modificare titolo, descrizione o priorità di un task già ARCHIVIATO.
Regola di business: un task archiviato è congelato e immutabile; per poterlo modificare
deve essere prima riaperto e riportato allo stato TODO.

Questo test verifica che tentativi di modifica su task ARCHIVED vengano bloccati con HTTP 422.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.regression
def test_regression_issue_101_cannot_modify_archived_task(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Verifica che un task archiviato non possa essere modificato finché rimane archiviato."""
    # 1. Creazione progetto e task
    proj = client.post("/api/v1/projects", json={"title": "Progetto Freeze"}, headers=auth_headers)
    project_id = proj.json()["id"]

    task = client.post(
        "/api/v1/tasks",
        json={"title": "Task da congelare", "project_id": project_id},
        headers=auth_headers,
    ).json()
    task_id = task["id"]

    # 2. Portiamo il task nello stato ARCHIVED
    arch_resp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "ARCHIVED"},
        headers=auth_headers,
    )
    assert arch_resp.status_code == 200
    assert arch_resp.json()["status"] == "ARCHIVED"

    # 3. Tentativo di modifica anagrafica (titolo/priorità) mentre è archiviato
    # COMPORTAMENTO ATTESO: Rifiuto con 422 Unprocessable Entity
    update_resp = client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Nuovo titolo illegale", "priority": "URGENT"},
        headers=auth_headers,
    )

    assert update_resp.status_code == 422, (
        f"Atteso 422 Unprocessable Entity per task archiviato, ricevuto {update_resp.status_code}: {update_resp.text}"
    )
    assert update_resp.json()["error"] == "INVALID_STATE_TRANSITION"
