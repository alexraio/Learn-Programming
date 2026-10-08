"""Schemi Pydantic per validazione e serializzazione dei progetti."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    """Campi base per un progetto."""

    title: str = Field(..., min_length=1, max_length=100, description="Titolo del progetto")
    description: str | None = Field(default=None, max_length=1000)


class ProjectCreate(ProjectBase):
    """Schema per la creazione di un progetto."""

    pass


class ProjectUpdate(BaseModel):
    """Schema per l'aggiornamento parziale di un progetto."""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class ProjectResponse(ProjectBase):
    """Schema di risposta per un progetto."""

    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
