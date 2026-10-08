"""Configurazione e gestione delle sessioni del database con SQLAlchemy 2.0."""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from taskmaster.core.config import get_settings

settings = get_settings()

# Per SQLite è necessario check_same_thread=False per permettere l'uso concorrente nei thread di FastAPI
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)


# Configurazione SQLite: abilitazione esplicita delle Foreign Keys e della modalità WAL
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: object, connection_record: object) -> None:
    """Configura i pragma SQLite per garantire integrità referenziale e concorrenza ottimale."""
    # Verifichiamo se l'oggetto connection supporta il metodo execute nativo di sqlite3
    cursor = getattr(dbapi_connection, "cursor", None)
    if cursor is not None:
        c = dbapi_connection.cursor()  # type: ignore[attr-defined]
        c.execute("PRAGMA foreign_keys=ON;")
        c.execute("PRAGMA journal_mode=WAL;")
        c.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Classe base dichiarativa per tutti i modelli ORM di SQLAlchemy."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency per FastAPI che produce una sessione transazionale isolata."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
