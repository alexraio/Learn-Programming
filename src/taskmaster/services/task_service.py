"""Logica di business per la gestione dei task e transizioni di stato."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskmaster.core.exceptions import EntityNotFoundError, InvalidStateTransitionError
from taskmaster.models.enums import TaskStatus
from taskmaster.models.project import Project
from taskmaster.models.task import Task
from taskmaster.schemas.task import TaskCreate, TaskUpdate
from taskmaster.services.project_service import get_project

# Regole formali di transizione consentite per gli stati dei task
VALID_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS, TaskStatus.ARCHIVED},
    TaskStatus.IN_PROGRESS: {TaskStatus.DONE, TaskStatus.TODO, TaskStatus.ARCHIVED},
    TaskStatus.DONE: {TaskStatus.ARCHIVED, TaskStatus.IN_PROGRESS},
    TaskStatus.ARCHIVED: {TaskStatus.TODO},  # Un task archiviato può essere solo riaperto in TODO
}


def create_task(db: Session, task_in: TaskCreate, current_user_id: int) -> Task:
    """Crea un nuovo task assicurandosi che il progetto esista e appartenga all'utente."""
    # Verifica preventiva di appartenenza del progetto genitore
    get_project(db, task_in.project_id, current_user_id)

    task = Task(
        title=task_in.title,
        description=task_in.description,
        status=TaskStatus.TODO,
        priority=task_in.priority,
        due_date=task_in.due_date,
        project_id=task_in.project_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int, current_user_id: int) -> Task:
    """Recupera un task assicurando che appartenga a un progetto dell'utente chiamante."""
    stmt = select(Task).join(Project).where(Task.id == task_id, Project.owner_id == current_user_id)
    task = db.scalars(stmt).first()
    if task is None:
        raise EntityNotFoundError("Task", task_id)
    return task


def list_tasks(
    db: Session,
    current_user_id: int,
    project_id: int | None = None,
    status: TaskStatus | None = None,
) -> list[Task]:
    """Elenca i task dell'utente con filtri opzionali per progetto e stato."""
    stmt = select(Task).join(Project).where(Project.owner_id == current_user_id)
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)

    stmt = stmt.order_by(Task.created_at.desc())
    return list(db.scalars(stmt).all())


def update_task_info(
    db: Session,
    task_id: int,
    task_in: TaskUpdate,
    current_user_id: int,
) -> Task:
    """Aggiorna i dati anagrafici del task (titolo, descrizione, priorità, scadenza)."""
    task = get_task(db, task_id, current_user_id)
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def update_task_status(
    db: Session,
    task_id: int,
    new_status: TaskStatus,
    current_user_id: int,
) -> Task:
    """Modifica lo stato del task validando le regole della macchina a stati."""
    task = get_task(db, task_id, current_user_id)

    if task.status == new_status:
        return task

    allowed_target_statuses = VALID_TRANSITIONS.get(task.status, set())
    if new_status not in allowed_target_statuses:
        raise InvalidStateTransitionError(task.status.value, new_status.value)

    task.status = new_status
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, current_user_id: int) -> None:
    """Elimina definitivamente un task dell'utente."""
    task = get_task(db, task_id, current_user_id)
    db.delete(task)
    db.commit()
