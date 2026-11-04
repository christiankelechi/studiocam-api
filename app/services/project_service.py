"""Project Management Business Service."""

from datetime import datetime
from typing import List, Optional
import uuid

from app.core.exceptions import ResourceNotFoundError
from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.repositories.project_repository import ProjectRepository, project_repository


class ProjectService:
    """Business logic for creative canvas projects."""

    def __init__(self, repo: ProjectRepository = project_repository):
        self.repo = repo

    def list_user_projects(self, user_id: str, include_trashed: bool = False) -> List[Project]:
        return self.repo.list_by_user(user_id, include_trashed=include_trashed)

    def get_project(self, project_id: str) -> Project:
        project = self.repo.get(project_id)
        if not project:
            raise ResourceNotFoundError("Project", project_id)
        return project

    def create_project(self, user_id: str, payload: ProjectCreate) -> Project:
        project_id = f"proj_{uuid.uuid4().hex[:10]}"
        title = payload.title or payload.name or "Untitled Studio Project"
        new_project = Project(
            id=project_id,
            user_id=user_id,
            title=title,
            name=title,
            aspect_ratio=payload.aspect_ratio,
            width=payload.width,
            height=payload.height,
            layers=payload.layers or [],
            tags=payload.tags or ["canvas"],
        )
        return self.repo.create(new_project)

    def update_project(self, project_id: str, payload: ProjectUpdate) -> Project:
        project = self.get_project(project_id)
        updates = payload.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.utcnow()
        updated = self.repo.update(project_id, updates)
        return updated or project

    def duplicate_project(self, project_id: str, user_id: str) -> Project:
        original = self.get_project(project_id)
        new_id = f"proj_{uuid.uuid4().hex[:10]}"
        clone = Project(
            id=new_id,
            user_id=user_id,
            title=f"{original.title} (Copy)",
            aspect_ratio=original.aspect_ratio,
            width=original.width,
            height=original.height,
            layers=original.layers,
            thumbnail_url=original.thumbnail_url,
            tags=original.tags,
        )
        return self.repo.create(clone)

    def soft_delete_project(self, project_id: str) -> bool:
        """Move project to 30-day trash archive."""
        return self.repo.update(project_id, {"is_trashed": True}) is not None

    def permanent_delete_project(self, project_id: str) -> bool:
        """Permanently delete project."""
        return self.repo.delete(project_id)


# Singleton service instance
project_service = ProjectService()

