"""Router per le operazioni di autenticazione e registrazione utente."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from taskmaster.core.database import get_db
from taskmaster.core.security import create_access_token
from taskmaster.schemas.token import Token
from taskmaster.schemas.user import UserCreate, UserLogin, UserResponse
from taskmaster.services.user_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrazione di un nuovo account utente",
)
def register(
    user_in: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Crea un nuovo account utente crittografando la password con Argon2."""
    user = create_user(db, user_in)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login OAuth2 (compatibile con Swagger UI e form-data)",
)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Emette un token JWT per il form di autenticazione standard OAuth2 (Swagger UI)."""
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/login/json",
    response_model=Token,
    summary="Login tramite JSON payload (per client API e frontend)",
)
def login_json(
    credentials: UserLogin,
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Emette un token JWT autenticando l'utente tramite payload JSON."""
    user = authenticate_user(db, email=credentials.email, password=credentials.password)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=access_token, token_type="bearer")
