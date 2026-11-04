"""Project and Canvas Canvas State Data Models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CanvasLayer(BaseModel):
    """Individual graphical layer on the StudioCam Engine canvas."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    id: str
    name: str
    type: str  # image, text, background, shadow, adjustment
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    blend_mode: str = Field(default="normal", alias="blendMode")
    data: Dict[str, Any] = Field(default_factory=dict)


class Project(BaseModel):
    """Domain model for a user's creative studio project."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    id: str
    user_id: str = Field(alias="userId", default="")
    title: str = "Untitled Project"
    name: Optional[str] = None  # Frontend convenience alias
    thumbnail_url: Optional[str] = Field(default=None, alias="thumbnailUrl")
    thumbnail: Optional[str] = None
    aspect_ratio: str = Field(default="1:1", alias="aspectRatio")
    width: int = 1080
    height: int = 1080
    layers: List[CanvasLayer] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")
    tags: List[str] = Field(default_factory=list)
    is_trashed: bool = Field(default=False, alias="isTrashed")
    message: Optional[str] = "Project retrieved successfully."
    success: bool = True


class ProjectCreate(BaseModel):
    """Payload to create a new project."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    title: str = "Untitled Studio Project"
    name: Optional[str] = None
    aspect_ratio: str = Field(default="1:1", alias="aspectRatio")
    width: int = 1080
    height: int = 1080
    layers: Optional[List[CanvasLayer]] = None
    tags: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    """Payload to update an existing project."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    title: Optional[str] = None
    name: Optional[str] = None
    aspect_ratio: Optional[str] = Field(default=None, alias="aspectRatio")
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail_url: Optional[str] = Field(default=None, alias="thumbnailUrl")
    layers: Optional[List[CanvasLayer]] = None
    tags: Optional[List[str]] = None
    is_trashed: Optional[bool] = Field(default=None, alias="isTrashed")

