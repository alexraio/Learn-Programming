"""Schemi Pydantic per token di autenticazione e payload JWT."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema di risposta per l'autenticazione con token Bearer."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema per il payload decodificato da un JWT."""

    sub: str | int
    exp: int | None = None
