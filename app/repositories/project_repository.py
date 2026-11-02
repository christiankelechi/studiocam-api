"""Project Repository implementing Project Data Access."""

from datetime import datetime
from typing import List, Optional
from app.models.project import CanvasLayer, Project
from app.repositories.base import ThreadSafeInMemoryRepository


class ProjectRepository(ThreadSafeInMemoryRepository[Project]):
    """Thread-safe Repository for Creative Projects."""

    def __init__(self):
        super().__init__()
        # Seed realistic initial projects
        self._seed_sample_projects()

    def _seed_sample_projects(self):
        sample_1 = Project(
            id="proj_office_campaign_01",
            user_id="usr_christian_001",
            title="Executive Suite Product Launch",
            thumbnail_url="https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=600&q=80",
            aspect_ratio="16:9",
            width=1920,
            height=1080,
            layers=[
                CanvasLayer(
                    id="layer_bg",
                    name="Modern Office Background",
                    type="background",
                    visible=True,
                    data={"prompt": "Modern executive glass corner office skyline"},
                ),
                CanvasLayer(
                    id="layer_subject",
                    name="Product Bottle",
                    type="image",
                    visible=True,
                    data={"x": 500, "y": 300, "scale": 1.0},
                ),
            ],
            tags=["office", "luxury", "campaign"],
        )

        sample_2 = Project(
            id="proj_headshot_boardroom_02",
            user_id="usr_christian_001",
            title="Executive Corporate Headshot",
            thumbnail_url="https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=600&q=80",
            aspect_ratio="1:1",
            width=1080,
            height=1080,
            layers=[
                CanvasLayer(
                    id="layer_bg_boardroom",
                    name="Boardroom Bokeh",
                    type="background",
                    visible=True,
                    data={"prompt": "Frosted glass corporate boardroom with soft bokeh"},
                )
            ],
            tags=["headshot", "corporate", "linkedin"],
        )

        self.create(sample_1)
        self.create(sample_2)

    def list_by_user(self, user_id: str, include_trashed: bool = False) -> List[Project]:
        """List active or trashed projects belonging to a user."""
        with self._lock:
            return [
                p
                for p in self._storage.values()
                if p.user_id == user_id and (p.is_trashed == include_trashed)
            ]


# Global singleton instance
project_repository = ProjectRepository()
