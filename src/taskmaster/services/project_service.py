"""Logica di business per la gestione dei progetti e dei relativi permessi."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskmaster.core.exceptions import EntityNotFoundError
from taskmaster.models.enums import TaskStatus
from taskmaster.models.project import Project
from taskmaster.models.task import Task
from taskmaster.schemas.project import ProjectCreate, ProjectStatsResponse, ProjectUpdate


def create_project(db: Session, project_in: ProjectCreate, owner_id: int) -> Project:
    """Crea un nuovo progetto assegnandolo all'utente proprietario specificato."""
    project = Project(
        title=project_in.title,
        description=project_in.description,
        owner_id=owner_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_user_projects(db: Session, owner_id: int) -> list[Project]:
    """Recupera tutti i progetti appartenenti all'utente specificato."""
    stmt = select(Project).where(Project.owner_id == owner_id).order_by(Project.created_at.desc())
    return list(db.scalars(stmt).all())


def get_project(db: Session, project_id: int, owner_id: int) -> Project:
    """Recupera un progetto per ID verificando che appartenga all'utente chiamante."""
    stmt = select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    project = db.scalars(stmt).first()
    if project is None:
        raise EntityNotFoundError("Progetto", project_id)
    return project


def update_project(
    db: Session,
    project_id: int,
    owner_id: int,
    project_in: ProjectUpdate,
) -> Project:
    """Aggiorna i campi di un progetto esistente se l'utente ne è il proprietario."""
    project = get_project(db, project_id, owner_id)
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, owner_id: int) -> None:
    """Elimina un progetto e tutti i suoi task in cascata."""
    project = get_project(db, project_id, owner_id)
    db.delete(project)
    db.commit()


def get_project_stats(db: Session, project_id: int, owner_id: int) -> ProjectStatsResponse:
    """Calcola le statistiche e la percentuale di completamento dei task di un progetto."""
    project = get_project(db, project_id, owner_id)
    stmt = select(Task).where(Task.project_id == project.id)
    tasks = list(db.scalars(stmt).all())

    total = len(tasks)
    todo_count = sum(1 for t in tasks if t.status == TaskStatus.TODO)
    in_progress_count = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
    done_count = sum(1 for t in tasks if t.status == TaskStatus.DONE)
    archived_count = sum(1 for t in tasks if t.status == TaskStatus.ARCHIVED)

    rate = round((done_count / total * 100.0), 2) if total > 0 else 0.0

    return ProjectStatsResponse(
        project_id=project.id,
        total_tasks=total,
        todo_count=todo_count,
        in_progress_count=in_progress_count,
        done_count=done_count,
        archived_count=archived_count,
        completion_rate=rate,
    )
