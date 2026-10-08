"""Test unitari parametrizzati con Pytest per la macchina a stati dei task."""

import pytest
from sqlalchemy.orm import Session

from taskmaster.core.exceptions import InvalidStateTransitionError
from taskmaster.models.enums import TaskStatus
from taskmaster.schemas.project import ProjectCreate
from taskmaster.schemas.task import TaskCreate
from taskmaster.schemas.user import UserCreate
from taskmaster.services.project_service import create_project
from taskmaster.services.task_service import create_task, update_task_status
from taskmaster.services.user_service import create_user


@pytest.fixture
def base_task(db_session: Session) -> tuple[int, int]:
    """Crea una base utente + progetto + task in stato TODO e restituisce (task_id, user_id)."""
    user = create_user(
        db_session,
        UserCreate(email="matrix@example.com", password="Password123!"),
    )
    project = create_project(
        db_session,
        ProjectCreate(title="Matrix Project"),
        owner_id=user.id,
    )
    task = create_task(
        db_session,
        TaskCreate(title="Base Task", project_id=project.id),
        current_user_id=user.id,
    )
    return task.id, user.id


def set_task_to_status(
    db: Session,
    task_id: int,
    target: TaskStatus,
    user_id: int,
) -> None:
    """Porta il task nello stato iniziale richiesto seguendo i passaggi legali."""
    if target == TaskStatus.TODO:
        return
    if target == TaskStatus.IN_PROGRESS:
        update_task_status(db, task_id, TaskStatus.IN_PROGRESS, user_id)
    elif target == TaskStatus.DONE:
        update_task_status(db, task_id, TaskStatus.IN_PROGRESS, user_id)
        update_task_status(db, task_id, TaskStatus.DONE, user_id)
    elif target == TaskStatus.ARCHIVED:
        update_task_status(db, task_id, TaskStatus.ARCHIVED, user_id)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("initial_status", "target_status"),
    [
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.TODO, TaskStatus.ARCHIVED),
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        (TaskStatus.IN_PROGRESS, TaskStatus.TODO),
        (TaskStatus.IN_PROGRESS, TaskStatus.ARCHIVED),
        (TaskStatus.DONE, TaskStatus.ARCHIVED),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
        (TaskStatus.ARCHIVED, TaskStatus.TODO),
    ],
)
def test_parameterized_allowed_transitions(
    db_session: Session,
    base_task: tuple[int, int],
    initial_status: TaskStatus,
    target_status: TaskStatus,
) -> None:
    """Verifica che tutte le combinazioni ammesse nella tabella di transizione abbiano successo."""
    task_id, user_id = base_task

    # Prepariamo lo stato iniziale in modo legale
    set_task_to_status(db_session, task_id, initial_status, user_id)

    # Eseguiamo la transizione verso il target
    updated = update_task_status(db_session, task_id, target_status, user_id)
    assert updated.status == target_status


@pytest.mark.unit
@pytest.mark.parametrize(
    ("initial_status", "forbidden_target"),
    [
        (TaskStatus.TODO, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.TODO),
        (TaskStatus.ARCHIVED, TaskStatus.IN_PROGRESS),
        (TaskStatus.ARCHIVED, TaskStatus.DONE),
    ],
)
def test_parameterized_forbidden_transitions(
    db_session: Session,
    base_task: tuple[int, int],
    initial_status: TaskStatus,
    forbidden_target: TaskStatus,
) -> None:
    """Verifica che le transizioni vietate sollevino puntualmente InvalidStateTransitionError."""
    task_id, user_id = base_task

    # Prepariamo lo stato iniziale
    set_task_to_status(db_session, task_id, initial_status, user_id)

    with pytest.raises(InvalidStateTransitionError):
        update_task_status(db_session, task_id, forbidden_target, user_id)
