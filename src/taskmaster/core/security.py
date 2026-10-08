"""Funzioni di utilità crittografica e sicurezza: password hashing e gestione JWT."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from taskmaster.core.config import get_settings

settings = get_settings()
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Calcola l'hash sicuro della password utilizzando l'algoritmo raccomandato (Argon2)."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica che la password in chiaro corrisponda all'hash memorizzato."""
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Crea e firma digitalmente un token JWT con payload e data di scadenza."""
    to_encode = data.copy()
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodifica e valida la firma e la scadenza di un token JWT."""
    payload: dict[str, Any] = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    return payload
