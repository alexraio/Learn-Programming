"""Enum tipizzati per stati e priorità dei task."""

from enum import StrEnum


class TaskStatus(StrEnum):
    """Stati ammessi nel ciclo di vita di un task."""

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"


class TaskPriority(StrEnum):
    """Livelli di priorità assegnabili a un task."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"
