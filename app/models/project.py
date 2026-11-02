"""Project and Canvas Canvas State Data Models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CanvasLayer(BaseModel):
    """Individual graphical layer on the Fabric.js canvas."""
    id: str
    name: str
    type: str  # image, text, background, shadow, adjustment
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    blend_mode: str = "normal"
    data: Dict[str, Any] = Field(default_factory=dict)


class Project(BaseModel):
    """Domain model for a user's creative studio project."""
    id: str
    user_id: str
    title: str
    thumbnail_url: Optional[str] = None
    aspect_ratio: str = "1:1"
    width: int = 1080
    height: int = 1080
    layers: List[CanvasLayer] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    is_trashed: bool = False


class ProjectCreate(BaseModel):
    """Payload to create a new project."""
    title: str = "Untitled Studio Project"
    aspect_ratio: str = "1:1"
    width: int = 1080
    height: int = 1080
    layers: Optional[List[CanvasLayer]] = None
    tags: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    """Payload to update an existing project."""
    title: Optional[str] = None
    aspect_ratio: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail_url: Optional[str] = None
    layers: Optional[List[CanvasLayer]] = None
    tags: Optional[List[str]] = None
    is_trashed: Optional[bool] = None

