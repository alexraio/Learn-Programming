"""Router per la gestione dei progetti."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from taskmaster.api.dependencies import get_current_user
from taskmaster.core.database import get_db
from taskmaster.models.user import User
from taskmaster.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatsResponse,
    ProjectUpdate,
)
from taskmaster.services.project_service import (
    create_project,
    delete_project,
    get_project,
    get_project_stats,
    get_user_projects,
    update_project,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuovo progetto",
)
def create_new_project(
    project_in: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectResponse:
    """Crea un nuovo progetto associato all'utente autenticato."""
    project = create_project(db, project_in, owner_id=current_user.id)
    return ProjectResponse.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="Elenca tutti i progetti dell'utente",
)
def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[ProjectResponse]:
    """Recupera la lista di tutti i progetti di proprietà dell'utente autenticato."""
    projects = get_user_projects(db, owner_id=current_user.id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Recupera un singolo progetto per ID",
)
def get_single_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectResponse:
    """Recupera i dettagli di un progetto verificando che appartenga all'utente."""
    project = get_project(db, project_id=project_id, owner_id=current_user.id)
    return ProjectResponse.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Aggiorna parzialmente un progetto",
)
def update_existing_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectResponse:
    """Aggiorna titolo o descrizione di un progetto esistente."""
    project = update_project(
        db,
        project_id=project_id,
        owner_id=current_user.id,
        project_in=project_in,
    )
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina un progetto e tutti i suoi task in cascata",
)
def remove_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Elimina definitivamente un progetto e i relativi task."""
    delete_project(db, project_id=project_id, owner_id=current_user.id)


@router.get(
    "/{project_id}/stats",
    response_model=ProjectStatsResponse,
    summary="Recupera le statistiche di avanzamento del progetto",
)
def get_single_project_stats(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectStatsResponse:
    """Restituisce il riepilogo dello stato dei task e la percentuale di completamento."""
    return get_project_stats(db, project_id=project_id, owner_id=current_user.id)
