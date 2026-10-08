"""Test di integrazione per gli endpoint di autenticazione (/api/v1/auth)."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_user_registration_success(client: TestClient) -> None:
    """Verifica la registrazione corretta di un nuovo utente (HTTP 201)."""
    payload = {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Nuovo Utente",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data
    assert "password" not in data  # Non dobbiamo mai esporre la password


@pytest.mark.integration
def test_user_registration_duplicate_email_conflict(client: TestClient) -> None:
    """Verifica che la registrazione con email già esistente risponda con HTTP 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "password": "SecurePassword123!",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    assert res2.json()["error"] == "DUPLICATE_ENTITY"


@pytest.mark.integration
def test_login_success_and_token_issuance(client: TestClient) -> None:
    """Verifica il corretto rilascio del token JWT al login."""
    # Registrazione preventiva
    client.post(
        "/api/v1/auth/register",
        json={"email": "loginuser@example.com", "password": "Password123!"},
    )

    # Login JSON
    response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "loginuser@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
def test_login_invalid_password_returns_401(client: TestClient) -> None:
    """Verifica che una password errata restituisca HTTP 401 Unauthorized."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpwd@example.com", "password": "Password123!"},
    )

    response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "wrongpwd@example.com", "password": "TotallyWrongPassword"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CREDENTIALS"


@pytest.mark.integration
def test_oauth2_form_login(client: TestClient) -> None:
    """Verifica il funzionamento del login tramite OAuth2PasswordRequestForm standard."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "formuser@example.com", "password": "Password123!"},
    )
    # Invio come form-data (username + password)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "formuser@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.integration
def test_access_protected_endpoint_without_or_with_invalid_token(client: TestClient) -> None:
    """Verifica che gli endpoint protetti rifiutino richieste senza token o con token alterato (401)."""
    # Nessun token
    res1 = client.get("/api/v1/projects")
    assert res1.status_code == 401

    # Token malformato
    res2 = client.get(
        "/api/v1/projects",
        headers={"Authorization": "Bearer token_completamente_invalido"},
    )
    assert res2.status_code == 401
