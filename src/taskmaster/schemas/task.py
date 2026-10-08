"""Schemi Pydantic per validazione e serializzazione dei task."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from taskmaster.models.enums import TaskPriority, TaskStatus


def validate_future_date(v: datetime | None) -> datetime | None:
    """Funzione di validazione riutilizzabile: impedisce date nel passato."""
    if v is not None:
        now = datetime.now(UTC)
        val_tz = v if v.tzinfo is not None else v.replace(tzinfo=UTC)
        if val_tz < now:
            raise ValueError("La data di scadenza (due_date) non può essere nel passato.")
    return v


class TaskBase(BaseModel):
    """Campi base per un task."""

    title: str = Field(..., min_length=1, max_length=200, description="Titolo del task")
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: datetime | None = None

    @field_validator("due_date")
    @classmethod
    def check_due_date(cls, v: datetime | None) -> datetime | None:
        """Verifica che la scadenza sia nel futuro."""
        return validate_future_date(v)


class TaskCreate(TaskBase):
    """Schema per la creazione di un task associato a un progetto."""

    project_id: int = Field(..., gt=0, description="ID del progetto genitore")


class TaskUpdate(BaseModel):
    """Schema per l'aggiornamento parziale dei campi informativi di un task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority | None = None
    due_date: datetime | None = None

    @field_validator("due_date")
    @classmethod
    def check_due_date(cls, v: datetime | None) -> datetime | None:
        """Verifica che la scadenza aggiornata sia nel futuro."""
        return validate_future_date(v)


class TaskStatusUpdate(BaseModel):
    """Schema dedicato all'aggiornamento controllato dello stato."""

    status: TaskStatus = Field(..., description="Nuovo stato del task")


class TaskResponse(TaskBase):
    """Schema di risposta per un task."""

    id: int
    status: TaskStatus
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
