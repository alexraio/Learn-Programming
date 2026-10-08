"""Test di integrazione per gli endpoint di gestione task (/api/v1/tasks)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_task_crud_and_status_transition_via_api(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Verifica il ciclo completo di vita di un task tramite chiamate HTTP REST."""
    # 1. Creazione Progetto
    proj_resp = client.post(
        "/api/v1/projects",
        json={"title": "Progetto Sprint 1"},
        headers=auth_headers,
    )
    assert proj_resp.status_code == 201
    project_id = proj_resp.json()["id"]

    # 2. Creazione Task
    task_payload = {
        "title": "Configurare CI/CD",
        "description": "Scrivere workflow GitHub Actions",
        "priority": "HIGH",
        "project_id": project_id,
    }
    create_task_resp = client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    assert create_task_resp.status_code == 201
    task_data = create_task_resp.json()
    task_id = task_data["id"]
    assert task_data["status"] == "TODO"

    # 3. Avanzamento di stato legale (TODO -> IN_PROGRESS)
    status_resp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=auth_headers,
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "IN_PROGRESS"

    # 4. Transizione illegale (IN_PROGRESS -> non è permesso un valore non riconosciuto o transizione non ammessa)
    invalid_resp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "NON_EXISTENT_STATUS"},
        headers=auth_headers,
    )
    assert invalid_resp.status_code == 422  # Validazione Pydantic

    # 5. Completamento del task (IN_PROGRESS -> DONE)
    done_resp = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "DONE"},
        headers=auth_headers,
    )
    assert done_resp.status_code == 200
    assert done_resp.json()["status"] == "DONE"

    # 6. Eliminazione del task
    del_resp = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    # 7. Verifica che il task non esista più
    get_del_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_del_resp.status_code == 404


@pytest.mark.integration
def test_task_filtering_and_update_info(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Verifica il filtro dei task per progetto/stato e l'aggiornamento dei metadati."""
    proj = client.post("/api/v1/projects", json={"title": "Progetto Filtri"}, headers=auth_headers)
    p_id = proj.json()["id"]

    t1 = client.post(
        "/api/v1/tasks",
        json={"title": "Task 1", "project_id": p_id},
        headers=auth_headers,
    ).json()
    client.post(
        "/api/v1/tasks",
        json={"title": "Task 2", "project_id": p_id},
        headers=auth_headers,
    )

    # Elenco filtrato per progetto
    list_resp = client.get(f"/api/v1/tasks?project_id={p_id}", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

    # Aggiorna info task
    update_resp = client.patch(
        f"/api/v1/tasks/{t1['id']}",
        json={"title": "Task 1 Modificato", "priority": "URGENT"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Task 1 Modificato"
    assert update_resp.json()["priority"] == "URGENT"
