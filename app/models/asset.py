"""Media Assets Data Models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Asset(BaseModel):
    """Domain model for a user's uploaded or generated media asset."""
    id: str
    user_id: str
    filename: str
    file_url: str
    thumbnail_url: Optional[str] = None
    file_type: str  # image/png, image/jpeg, video/mp4
    size_bytes: int
    width: Optional[int] = None
    height: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AssetUploadResponse(BaseModel):
    """Response returned upon uploading an asset."""
    asset: Asset
    message: str = "Asset uploaded successfully"

