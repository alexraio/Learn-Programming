"""Schemi Pydantic per validazione e serializzazione degli utenti."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Campi comuni per gli utenti."""

    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Schema per la registrazione di un nuovo utente."""

    password: str = Field(..., min_length=8, description="Password di almeno 8 caratteri")


class UserLogin(BaseModel):
    """Schema per il login utente con email e password."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema di risposta sicuro (non espone la password hashata)."""

    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
