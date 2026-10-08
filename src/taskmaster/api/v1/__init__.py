"""Router principale per API Versione 1."""

from fastapi import APIRouter

from taskmaster.api.v1.auth import router as auth_router
from taskmaster.api.v1.projects import router as projects_router
from taskmaster.api.v1.tasks import router as tasks_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(tasks_router)
