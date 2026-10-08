"""Logica di business per la gestione degli utenti e l'autenticazione."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskmaster.core.exceptions import DuplicateEntityError, InvalidCredentialsError
from taskmaster.core.security import hash_password, verify_password
from taskmaster.models.user import User
from taskmaster.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    """Cerca un utente tramite indirizzo email."""
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Cerca un utente tramite ID primario."""
    stmt = select(User).where(User.id == user_id)
    return db.scalars(stmt).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Registra un nuovo utente garantendo l'unicità dell'email e l'hashing della password."""
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user is not None:
        raise DuplicateEntityError(f"Un account con email '{user_in.email}' esiste già.")

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Autentica l'utente confrontando la password con l'hash memorizzato."""
    user = get_user_by_email(db, email)
    if user is None:
        raise InvalidCredentialsError("Email o password non corretti.")

    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Email o password non corretti.")

    if not user.is_active:
        raise InvalidCredentialsError("Questo account utente è disattivato.")

    return user
