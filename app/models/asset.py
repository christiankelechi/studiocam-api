"""Media Assets Data Models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Asset(BaseModel):
    """Domain model for a user's uploaded or generated media asset."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    user_id: str = Field(..., alias="userId")
    filename: str = Field(..., alias="name")
    file_url: str = Field(..., alias="url")
    thumbnail_url: Optional[str] = Field(None, alias="thumbnailUrl")
    file_type: str = Field("image/png", alias="type")  # image/png, image/jpeg, video/mp4
    size_bytes: int = Field(0, alias="sizeBytes")
    width: Optional[int] = None
    height: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")


class AssetUploadResponse(BaseModel):
    """Response returned upon uploading an asset."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    asset: Asset
    message: str = "Asset uploaded successfully"

