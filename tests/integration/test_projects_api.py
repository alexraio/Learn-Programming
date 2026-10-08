"""Test di integrazione per gli endpoint di gestione progetti (/api/v1/projects)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_create_and_get_project(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Verifica la creazione di un progetto e il suo successivo recupero."""
    payload = {"title": "Nuovo Progetto Backend", "description": "Descrizione progetto"}
    create_resp = client.post("/api/v1/projects", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["title"] == payload["title"]
    assert "id" in created_data

    # Recupero lista
    list_resp = client.get("/api/v1/projects", headers=auth_headers)
    assert list_resp.status_code == 200
    projects = list_resp.json()
    assert len(projects) == 1
    assert projects[0]["id"] == created_data["id"]


@pytest.mark.integration
def test_user_cannot_access_other_users_project(
    client: TestClient,
    auth_headers: dict[str, str],
    second_user_headers: dict[str, str],
) -> None:
    """Verifica la segregazione dei dati: l'utente B non deve poter accedere al progetto dell'utente A (404)."""
    # Utente A crea il suo progetto
    payload = {"title": "Progetto Privato Utente A"}
    create_resp = client.post("/api/v1/projects", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    # Utente B tenta di accedere al progetto di A
    access_resp = client.get(f"/api/v1/projects/{project_id}", headers=second_user_headers)
    assert access_resp.status_code == 404
    assert access_resp.json()["error"] == "ENTITY_NOT_FOUND"


@pytest.mark.integration
def test_update_and_delete_project(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Verifica l'aggiornamento e l'eliminazione a cascata di un progetto."""
    create_resp = client.post(
        "/api/v1/projects",
        json={"title": "Progetto da modificare", "description": "Vecchia desc"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    # Patch
    patch_resp = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"title": "Progetto Rinominato"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "Progetto Rinominato"

    # Delete
    del_resp = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert del_resp.status_code == 204

    # Verifica rimozione
    get_resp = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert get_resp.status_code == 404
