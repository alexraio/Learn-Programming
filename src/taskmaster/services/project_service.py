"""Logica di business per la gestione dei progetti e dei relativi permessi."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskmaster.core.exceptions import EntityNotFoundError
from taskmaster.models.project import Project
from taskmaster.schemas.project import ProjectCreate, ProjectUpdate


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
