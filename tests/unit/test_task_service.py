"""Test unitari per la macchina a stati e la logica del servizio task."""

import pytest
from sqlalchemy.orm import Session

from taskmaster.core.exceptions import InvalidStateTransitionError
from taskmaster.models.enums import TaskPriority, TaskStatus
from taskmaster.schemas.project import ProjectCreate
from taskmaster.schemas.task import TaskCreate
from taskmaster.schemas.user import UserCreate
from taskmaster.services.project_service import create_project
from taskmaster.services.task_service import create_task, update_task_status
from taskmaster.services.user_service import create_user


@pytest.mark.unit
def test_valid_task_state_transitions(db_session: Session) -> None:
    """Verifica le transizioni di stato legali: TODO -> IN_PROGRESS -> DONE -> ARCHIVED -> TODO."""
    # Setup dati
    user = create_user(
        db_session,
        UserCreate(email="author@example.com", password="Password123!"),
    )
    project = create_project(
        db_session,
        ProjectCreate(title="Test Project"),
        owner_id=user.id,
    )
    task = create_task(
        db_session,
        TaskCreate(
            title="Initial Task",
            project_id=project.id,
            priority=TaskPriority.HIGH,
        ),
        current_user_id=user.id,
    )

    assert task.status == TaskStatus.TODO

    # TODO -> IN_PROGRESS
    task = update_task_status(
        db_session,
        task_id=task.id,
        new_status=TaskStatus.IN_PROGRESS,
        current_user_id=user.id,
    )
    assert task.status == TaskStatus.IN_PROGRESS

    # IN_PROGRESS -> DONE
    task = update_task_status(
        db_session,
        task_id=task.id,
        new_status=TaskStatus.DONE,
        current_user_id=user.id,
    )
    assert task.status == TaskStatus.DONE

    # DONE -> ARCHIVED
    task = update_task_status(
        db_session,
        task_id=task.id,
        new_status=TaskStatus.ARCHIVED,
        current_user_id=user.id,
    )
    assert task.status == TaskStatus.ARCHIVED

    # ARCHIVED -> TODO (Riapertura)
    task = update_task_status(
        db_session,
        task_id=task.id,
        new_status=TaskStatus.TODO,
        current_user_id=user.id,
    )
    assert task.status == TaskStatus.TODO


@pytest.mark.unit
def test_invalid_task_state_transition_raises_error(db_session: Session) -> None:
    """Verifica che una transizione illegale (ARCHIVED -> DONE) sollevi InvalidStateTransitionError."""
    user = create_user(
        db_session,
        UserCreate(email="author2@example.com", password="Password123!"),
    )
    project = create_project(
        db_session,
        ProjectCreate(title="Test Project"),
        owner_id=user.id,
    )
    task = create_task(
        db_session,
        TaskCreate(title="Task to Archive", project_id=project.id),
        current_user_id=user.id,
    )

    # Portiamo il task direttamente in ARCHIVED
    task = update_task_status(
        db_session,
        task_id=task.id,
        new_status=TaskStatus.ARCHIVED,
        current_user_id=user.id,
    )
    assert task.status == TaskStatus.ARCHIVED

    # Tentativo non consentito: da ARCHIVED a DONE
    with pytest.raises(InvalidStateTransitionError):
        update_task_status(
            db_session,
            task_id=task.id,
            new_status=TaskStatus.DONE,
            current_user_id=user.id,
        )
