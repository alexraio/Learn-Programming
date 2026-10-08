"""Router per la gestione dei task e aggiornamento degli stati."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from taskmaster.api.dependencies import get_current_user
from taskmaster.core.database import get_db
from taskmaster.models.enums import TaskStatus
from taskmaster.models.user import User
from taskmaster.schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate, TaskUpdate
from taskmaster.services.task_service import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    update_task_info,
    update_task_status,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuovo task",
)
def create_new_task(
    task_in: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """Crea un nuovo task all'interno di un progetto di proprietà dell'utente."""
    task = create_task(db, task_in=task_in, current_user_id=current_user.id)
    return TaskResponse.model_validate(task)


@router.get(
    "",
    response_model=list[TaskResponse],
    summary="Elenca i task con filtri opzionali",
)
def get_all_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    project_id: Annotated[int | None, Query(description="Filtra per ID progetto")] = None,
    status_filter: Annotated[
        TaskStatus | None,
        Query(alias="status", description="Filtra per stato del task"),
    ] = None,
) -> list[TaskResponse]:
    """Elenca tutti i task dell'utente con possibilità di filtrare per progetto o stato."""
    tasks = list_tasks(
        db,
        current_user_id=current_user.id,
        project_id=project_id,
        status=status_filter,
    )
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Recupera un singolo task per ID",
)
def get_single_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """Recupera un task verificando che appartenga a un progetto dell'utente."""
    task = get_task(db, task_id=task_id, current_user_id=current_user.id)
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Aggiorna metadati di un task",
)
def update_task_details(
    task_id: int,
    task_in: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """Aggiorna titolo, descrizione, priorità o scadenza di un task."""
    task = update_task_info(
        db,
        task_id=task_id,
        task_in=task_in,
        current_user_id=current_user.id,
    )
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
    summary="Aggiorna lo stato di un task secondo la macchina a stati",
)
def change_task_status(
    task_id: int,
    status_in: TaskStatusUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """Aggiorna lo stato di avanzamento applicando le regole di transizione ammesse."""
    task = update_task_status(
        db,
        task_id=task_id,
        new_status=status_in.status,
        current_user_id=current_user.id,
    )
    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina un task",
)
def remove_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Elimina definitivamente un task appartenente all'utente."""
    delete_task(db, task_id=task_id, current_user_id=current_user.id)
