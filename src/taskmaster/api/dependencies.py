"""Iniezione delle dipendenze per FastAPI: sessione DB e autenticazione utente."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from taskmaster.core.config import get_settings
from taskmaster.core.database import get_db
from taskmaster.core.security import decode_access_token
from taskmaster.models.user import User
from taskmaster.services.user_service import get_user_by_id

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login",
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Valida il token Bearer JWT e restituisce l'istanza dell'utente autenticato."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token di autenticazione non valido o scaduto.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception from None

    user = get_user_by_id(db, user_id=user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user
