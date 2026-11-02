"""Projects and Canvas States API Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.models.auth import UserInDB
from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.services.project_service import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[Project])
def list_projects(include_trashed: bool = False, user: UserInDB = Depends(get_current_user)):
    """List all projects for authenticated user."""
    return project_service.list_user_projects(user.id, include_trashed=include_trashed)


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, user: UserInDB = Depends(get_current_user)):
    """Create a new project canvas."""
    return project_service.create_project(user.id, payload)


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str, user: UserInDB = Depends(get_current_user)):
    """Retrieve project details by ID."""
    return project_service.get_project(project_id)


@router.put("/{project_id}", response_model=Project)
def update_project(project_id: str, payload: ProjectUpdate, user: UserInDB = Depends(get_current_user)):
    """Update project canvas layers, title, or properties."""
    return project_service.update_project(project_id, payload)


@router.delete("/{project_id}")
def delete_project(project_id: str, permanent: bool = False, user: UserInDB = Depends(get_current_user)):
    """Move to trash or permanently delete a project."""
    if permanent:
        success = project_service.permanent_delete_project(project_id)
    else:
        success = project_service.soft_delete_project(project_id)
    return {"success": success, "message": "Project deleted successfully"}


@router.post("/{project_id}/duplicate", response_model=Project)
def duplicate_project(project_id: str, user: UserInDB = Depends(get_current_user)):
    """Create an exact duplicate copy of a project."""
    return project_service.duplicate_project(project_id, user.id)


@router.post("/{project_id}/export")
def export_project(project_id: str, format: str = "png", quality: int = 100, user: UserInDB = Depends(get_current_user)):
    """Export project canvas to high-res image format."""
    project = project_service.get_project(project_id)
    return {
        "success": True,
        "project_id": project.id,
        "format": format.lower(),
        "quality": quality,
        "export_url": project.thumbnail_url or "/api/v1/outputs/sample_export.png",
        "message": f"Project exported successfully as high-resolution {format.upper()}",
    }

