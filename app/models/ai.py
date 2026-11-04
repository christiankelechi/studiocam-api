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
    success: bool = True
    message: Optional[str] = "Job status retrieved successfully."


class BgRemovalRequest(BaseModel):
    """Payload for StudioCam Smart Cutout™ subject cutout."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    feather_radius: float = Field(default=2.0, alias="featherRadius")
    return_mask: bool = Field(default=False, alias="returnMask")


class SceneSwapRequest(BaseModel):
    """Payload for StudioCam UltraScene™ photorealistic scene & office generation."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    prompt: Optional[str] = "Modern executive CEO office with floor-to-ceiling glass windows overlooking skyline, warm ambient desk lighting, cinematic 8k"
    preset_category: Optional[str] = Field(default="office", alias="presetCategory")
    preset_id: Optional[str] = Field(default="executive_penthouse", alias="presetId")
    shadow_softness: float = Field(default=0.5, alias="shadowSoftness")
    light_direction: float = Field(default=45.0, alias="lightDirection")
    color_harmonization: float = Field(default=0.7, alias="colorHarmonization")


class RelightRequest(BaseModel):
    """Payload for StudioCam CinemaLight™ studio directional relighting."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    light_angle: float = Field(default=45.0, alias="lightAngle")
    light_intensity: float = Field(default=1.0, alias="lightIntensity")
    color_temperature: int = Field(default=4500, alias="colorTemperature")
    ambient_exposure: float = Field(default=0.0, alias="ambientExposure")
    light_color_hex: Optional[str] = Field(default="#FFFFFF", alias="lightColorHex")


class VideoAnimateRequest(BaseModel):
    """Payload for StudioCam CinemaMotion™ / StudioCam CinemaMotion™ cinematic image-to-video motion synthesis."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    motion_type: str = Field(default="cinematic_push_in", alias="motionType")
    duration_seconds: int = Field(default=5, alias="durationSeconds")
    fps: int = 24
    camera_intensity: float = Field(default=0.8, alias="cameraIntensity")
    motion_prompt: Optional[str] = Field(default="Subtle cinematic motion, slow depth-of-field rack focus", alias="motionPrompt")


class MagicEraseRequest(BaseModel):
    """Payload for AI brush cleanup & object inpainting."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    mask_base64: Optional[str] = Field(default=None, alias="maskBase64")
    mask_data_url: Optional[str] = Field(default=None, alias="maskDataUrl")
    prompt: Optional[str] = "clean seamless background texture, remove unwanted object"


class UpscaleRequest(BaseModel):
    """Payload for AI 4K/8K Super Resolution."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    scale_factor: int = Field(default=4, alias="scaleFactor")
    factor: Optional[int] = None
    denoise_strength: float = Field(default=0.3, alias="denoiseStrength")
    face_restore: bool = Field(default=True, alias="faceRestore")


class FaceRestoreRequest(BaseModel):
    """Payload for StudioCam Face Clarity Engine™ / StudioCam Face Clarity Engine™ facial clarity restoration."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    image_base64: Optional[str] = Field(default=None, alias="imageBase64")
    fidelity_ratio: float = Field(default=0.8, alias="fidelityRatio")


class NLPCommandRequest(BaseModel):
    """Natural Language Voice/Text input transcript to be routed into UI action directives."""
    model_config = {"populate_by_name": True, "extra": "ignore"}
    transcript: Optional[str] = None
    command_text: Optional[str] = Field(default=None, alias="commandText")
    current_context: Optional[Dict[str, Any]] = Field(default=None, alias="currentContext")

    def get_text(self) -> str:
        return self.transcript or self.command_text or ""


class NLPCommandResponse(BaseModel):
    """Structured action directive parsed by NLP engine."""
    recognized_intent: str  # remove_background, change_scene, relight, animate, export, undo
    confidence: float
    target_tool: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    friendly_response: str
    executed_action: bool = True
    success: bool = True
    message: str = "Command successfully parsed and routed."

