"""Media Asset Management Service."""

import os
import uuid
from typing import List
from PIL import Image

from app.core.config import settings
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository, asset_repository


class AssetService:
    """Business logic for uploading, organizing, and serving media assets."""

    def __init__(self, repo: AssetRepository = asset_repository):
        self.repo = repo

    def list_user_assets(self, user_id: str) -> List[Asset]:
        return self.repo.list_by_user(user_id)

    def save_uploaded_file(self, user_id: str, filename: str, content: bytes, content_type: str) -> Asset:
        """Store uploaded file on disk and index in asset repository."""
        asset_id = f"ast_{uuid.uuid4().hex[:10]}"
        ext = os.path.splitext(filename)[1] or ".png"
        saved_filename = f"{asset_id}{ext}"
        filepath = os.path.join(settings.UPLOADS_PATH, saved_filename)

        with open(filepath, "wb") as f:
            f.write(content)

        width, height = None, None
        try:
            with Image.open(filepath) as img:
                width, height = img.size
        except Exception:
            pass

        asset = Asset(
            id=asset_id,
            user_id=user_id,
            filename=filename,
            file_url=f"/api/v1/uploads/{saved_filename}",
            thumbnail_url=f"/api/v1/uploads/{saved_filename}",
            file_type=content_type,
            size_bytes=len(content),
            width=width,
            height=height,
            tags=["upload"],
        )
        return self.repo.create(asset)

    def delete_asset(self, asset_id: str) -> bool:
        return self.repo.delete(asset_id)


# Singleton service instance
asset_service = AssetService()

