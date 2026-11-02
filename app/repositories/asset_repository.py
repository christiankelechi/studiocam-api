"""Media Asset Repository implementing Asset Data Access."""

from typing import List
from app.models.asset import Asset
from app.repositories.base import ThreadSafeInMemoryRepository


class AssetRepository(ThreadSafeInMemoryRepository[Asset]):
    """Thread-safe Repository for Media Assets."""

    def __init__(self):
        super().__init__()
        # Seed realistic asset library
        self._seed_sample_assets()

    def _seed_sample_assets(self):
        asset_1 = Asset(
            id="ast_office_desk_01",
            user_id="usr_christian_001",
            filename="executive_marble_desk.jpg",
            file_url="https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=800&q=80",
            thumbnail_url="https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=256&q=80",
            file_type="image/jpeg",
            size_bytes=1048576,
            width=1920,
            height=1080,
            tags=["office", "interior", "executive"],
        )
        asset_2 = Asset(
            id="ast_glass_building_02",
            user_id="usr_christian_001",
            filename="skyscrapers_window_view.jpg",
            file_url="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
            thumbnail_url="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=256&q=80",
            file_type="image/jpeg",
            size_bytes=2097152,
            width=2400,
            height=1600,
            tags=["architecture", "skyline", "modern"],
        )
        self.create(asset_1)
        self.create(asset_2)

    def list_by_user(self, user_id: str) -> List[Asset]:
        """List assets belonging to a user."""
        with self._lock:
            return [a for a in self._storage.values() if a.user_id == user_id]


# Global singleton instance
asset_repository = AssetRepository()

