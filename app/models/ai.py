"""AI Pipelines & Generative Operations Data Models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationJob(BaseModel):
    """Represents an asynchronous AI GPU pipeline generation job."""
    id: str
    user_id: str
    pipeline: str  # remove-bg, scene-swap, relight, animate, magic-erase, upscale
    status: JobStatus = JobStatus.QUEUED
    progress: int = 0  # 0 to 100%
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_url: Optional[str] = None
    output_preview: Optional[str] = None  # Base64 or thumbnail
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class BgRemovalRequest(BaseModel):
    """Payload for BRIA RMBG-1.4 subject cutout."""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    feather_radius: float = 2.0
    return_mask: bool = False


class SceneSwapRequest(BaseModel):
    """Payload for Flux.1 photorealistic scene & office generation."""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    prompt: str = "Modern executive CEO office with floor-to-ceiling glass windows overlooking skyline, warm ambient desk lighting, cinematic 8k"
    preset_category: Optional[str] = "office"  # office, studio, outdoor, architectural, abstract
    preset_id: Optional[str] = "executive_penthouse"  # executive_penthouse, modern_open_workspace, minimalist_scandinavian, etc.
    shadow_softness: float = 0.5
    light_direction: float = 45.0  # degrees 0-360
    color_harmonization: float = 0.7


class RelightRequest(BaseModel):
    """Payload for IC-Light studio directional relighting."""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    light_angle: float = 45.0  # degrees 0 - 360
    light_intensity: float = 1.0  # 0.0 - 2.0
    color_temperature: int = 4500  # 2500K (warm) to 7500K (cool)
    ambient_exposure: float = 0.0  # -1.0 to 1.0
    light_color_hex: Optional[str] = "#FFFFFF"


class VideoAnimateRequest(BaseModel):
    """Payload for Wan 2.1 / LTX-2 cinematic image-to-video motion synthesis."""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    motion_type: str = "cinematic_push_in"  # push_in, pan_right, orbit, tilt_up, slow_zoom
    duration_seconds: int = 5
    fps: int = 24
    camera_intensity: float = 0.8
    motion_prompt: Optional[str] = "Subtle cinematic motion, slow depth-of-field rack focus"


class MagicEraseRequest(BaseModel):
    """Payload for AI brush cleanup & object inpainting."""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    mask_base64: Optional[str] = None
    prompt: Optional[str] = "clean seamless background texture, remove unwanted object"


class UpscaleRequest(BaseModel):
    """Payload for AI 4K/8K Super Resolution."""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    scale_factor: int = 4  # 2x, 4x, 8x
    denoise_strength: float = 0.3


class FaceRestoreRequest(BaseModel):
    """Payload for GFPGAN / CodeFormer facial clarity restoration."""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    fidelity_ratio: float = 0.8


class NLPCommandRequest(BaseModel):
    """Natural Language Voice/Text input transcript to be routed into UI action directives."""
    transcript: str
    current_context: Optional[Dict[str, Any]] = None


class NLPCommandResponse(BaseModel):
    """Structured action directive parsed by NLP engine."""
    recognized_intent: str  # remove_background, change_scene, relight, animate, export, undo
    confidence: float
    target_tool: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    friendly_response: str
    executed_action: bool = True

