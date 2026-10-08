"""Fixtures condivise per la suite di test Pytest con DB SQLite isolato in memoria."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from taskmaster.core.database import Base, get_db
from taskmaster.main import app

# Configurazione di un database SQLite in memoria dedicato ai test (StaticPool garantisce persistenza nella sessione di test)
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def setup_test_db() -> Generator[None, None, None]:
    """Crea tutte le tabelle prima di ogni test e le distrugge al termine."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Restituisce una sessione database isolata per i test di servizio."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient con dependency override per usare il database in memoria."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Registra un utente di test, effettua il login e restituisce gli header con il token Bearer."""
    user_payload = {
        "email": "testuser@example.com",
        "password": "Password123!",
        "full_name": "Test User",
    }
    # Registrazione
    reg_resp = client.post("/api/v1/auth/register", json=user_payload)
    assert reg_resp.status_code == 201

    # Login
    login_resp = client.post(
        "/api/v1/auth/login/json",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_headers(client: TestClient) -> dict[str, str]:
    """Registra un secondo utente per testare la segregazione e i permessi."""
    user_payload = {
        "email": "second@example.com",
        "password": "Password123!",
        "full_name": "Second User",
    }
    reg_resp = client.post("/api/v1/auth/register", json=user_payload)
    assert reg_resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login/json",
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
