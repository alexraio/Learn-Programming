"""Entry point principale dell'applicazione TaskMaster API."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from taskmaster.api.v1 import api_v1_router
from taskmaster.core.config import get_settings
from taskmaster.core.database import Base, engine
from taskmaster.core.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    InvalidCredentialsError,
    InvalidStateTransitionError,
    PermissionDeniedError,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestione del ciclo di vita dell'applicazione: inizializzazione tabelle DB."""
    # Inizializza le tabelle all'avvio dell'applicazione
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    description="API REST professionale per la gestione di progetti e task con autenticazione JWT",
    version=settings.app_version,
    lifespan=lifespan,
)

# Registrazione router API v1
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


# Exception Handlers Centralizzati
@app.exception_handler(EntityNotFoundError)
def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
    """Mappa l'errore di entità non trovata a HTTP 404 Not Found."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": exc.code, "detail": exc.message},
    )


@app.exception_handler(DuplicateEntityError)
def duplicate_entity_handler(request: Request, exc: DuplicateEntityError) -> JSONResponse:
    """Mappa duplicazioni univoche a HTTP 409 Conflict."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": exc.code, "detail": exc.message},
    )


@app.exception_handler(InvalidCredentialsError)
def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
    """Mappa credenziali errate a HTTP 401 Unauthorized."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": exc.code, "detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(PermissionDeniedError)
def permission_denied_handler(request: Request, exc: PermissionDeniedError) -> JSONResponse:
    """Mappa violazioni di permessi a HTTP 403 Forbidden."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": exc.code, "detail": exc.message},
    )


@app.exception_handler(InvalidStateTransitionError)
def invalid_state_transition_handler(
    request: Request,
    exc: InvalidStateTransitionError,
) -> JSONResponse:
    """Mappa tentativi di transizione di stato non consentiti a HTTP 422 Unprocessable Entity."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": exc.code, "detail": exc.message},
    )


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Endpoint di health check per verificare che il servizio sia operativo."""
    return {"status": "healthy", "service": "taskmaster-api", "version": settings.app_version}


def main() -> None:
    """Funzione di avvio per il comando CLI uv run taskmaster."""
    uvicorn.run("taskmaster.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
