"""API v1 Consolidated Router."""

from fastapi import APIRouter
from app.api.v1.ai import router as ai_router
from app.api.v1.assets import router as assets_router
from app.api.v1.auth import router as auth_router
from app.api.v1.billing import router as billing_router
from app.api.v1.projects import router as projects_router
from app.api.v1.system import router as system_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(ai_router)
api_router.include_router(assets_router)
api_router.include_router(billing_router)
api_router.include_router(system_router)

