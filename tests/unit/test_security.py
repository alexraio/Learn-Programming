"""Test unitari per il modulo di sicurezza e crittografia."""

from datetime import timedelta

import jwt
import pytest

from taskmaster.core.config import get_settings
from taskmaster.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

settings = get_settings()


@pytest.mark.unit
def test_password_hashing_and_verification() -> None:
    """Verifica che l'hashing generi una stringa sicura e la validi correttamente."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    # L'hash non deve coincidere con la password in chiaro
    assert hashed != password
    # La verifica con la password corretta deve riuscire
    assert verify_password(password, hashed) is True
    # La verifica con una password errata deve fallire
    assert verify_password("WrongPassword123!", hashed) is False


@pytest.mark.unit
def test_jwt_token_lifecycle() -> None:
    """Verifica la creazione e decodifica di un token JWT valido."""
    payload = {"sub": "42", "role": "admin"}
    token = create_access_token(data=payload, expires_delta=timedelta(minutes=15))

    decoded = decode_access_token(token)
    assert decoded["sub"] == "42"
    assert decoded["role"] == "admin"
    assert "exp" in decoded


@pytest.mark.unit
def test_jwt_token_expired() -> None:
    """Verifica che un token scaduto sollevi l'eccezione PyJWTError appropriata."""
    payload = {"sub": "42"}
    # Creiamo un token scaduto nel passato (-10 minuti)
    expired_token = create_access_token(data=payload, expires_delta=timedelta(minutes=-10))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)
