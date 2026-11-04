"""Natural Language Voice & Text Command Router Service."""

import re
from typing import Any, Dict
from app.models.ai import NLPCommandRequest, NLPCommandResponse
from app.models.auth import UserInDB
from app.services.ai.base_engine import BaseAIEngine


class NLPCommandRouterEngine(BaseAIEngine):
    """
    Intelligent NLP Intent Classifier & Command Router.
    Parses conversational voice transcripts and text prompts into structured UI execution directives.
    """

    @property
    def engine_name(self) -> str:
        return "StudioCam Neural NLP Command Router"

    @property
    def credit_cost(self) -> int:
        return 0  # Voice parsing is free for all users

    def validate_input(self, request_data: NLPCommandRequest) -> None:
        text = request_data.get_text()
        if not text or not text.strip():
            raise ValueError("Transcript cannot be empty.")

    def execute_pipeline(self, request_data: NLPCommandRequest, user: UserInDB) -> Dict[str, Any]:
        """Classify user intent and extract parameterized UI directives."""
        transcript = request_data.get_text().lower().strip()

        # 1. Background Removal Intent
        if any(w in transcript for w in ("remove background", "cut out", "isolate", "transparent", "rmbg", "remove bg")):
            return NLPCommandResponse(
                recognized_intent="remove_background",
                confidence=0.98,
                target_tool="bg_remover",
                parameters={"feather_radius": 2.0},
                friendly_response="Isolating the subject with StudioCam Smart Cutout™ alpha matting.",
                executed_action=True,
            ).model_dump()

        # 2. Scene Swap / Office Placement Intent
        if any(w in transcript for w in ("scene", "office", "boardroom", "background", "workspace", "penthouse", "studio", "environment")):
            preset_id = "executive_penthouse"
            if "minimal" in transcript or "scandinavian" in transcript:
                preset_id = "minimalist_scandinavian"
            elif "tech" in transcript or "silicon" in transcript:
                preset_id = "tech_innovation_lab"
            elif "loft" in transcript or "brick" in transcript:
                preset_id = "creative_loft_studio"
            elif "boardroom" in transcript or "conference" in transcript:
                preset_id = "boardroom_conference"
            elif "home" in transcript:
                preset_id = "modern_home_office"

            return NLPCommandResponse(
                recognized_intent="scene_swap",
                confidence=0.95,
                target_tool="scene_swap",
                parameters={
                    "preset_id": preset_id,
                    "prompt": request_data.get_text(),
                    "shadow_softness": 0.6,
                },
                friendly_response=f"Generating photorealistic scene using the {preset_id.replace('_', ' ').title()} environment.",
                executed_action=True,
            ).model_dump()

        # 3. Relighting Intent
        if any(w in transcript for w in ("light", "relight", "warm", "cool", "shadow", "sunlight", "golden")):
            angle = 45.0
            temp = 4500
            if "warm" in transcript or "golden" in transcript or "sunset" in transcript:
                temp = 3200
            elif "cool" in transcript or "blue" in transcript or "daylight" in transcript:
                temp = 6500

            if "left" in transcript:
                angle = 135.0
            elif "top" in transcript:
                angle = 90.0
            elif "right" in transcript:
                angle = 45.0

            return NLPCommandResponse(
                recognized_intent="relight",
                confidence=0.92,
                target_tool="relighting",
                parameters={
                    "light_angle": angle,
                    "color_temperature": temp,
                    "light_intensity": 1.2,
                },
                friendly_response=f"Adjusting directional illumination to {angle}° at {temp}K color temperature.",
                executed_action=True,
            ).model_dump()

        # 4. Video Animation Intent
        if any(w in transcript for w in ("animate", "video", "motion", "cinematic", "move", "pan", "zoom")):
            motion = "cinematic_push_in"
            if "pan" in transcript:
                motion = "pan_right"
            elif "orbit" in transcript:
                motion = "orbit"
            elif "tilt" in transcript:
                motion = "tilt_up"

            return NLPCommandResponse(
                recognized_intent="animate",
                confidence=0.94,
                target_tool="animator",
                parameters={
                    "motion_type": motion,
                    "duration_seconds": 5,
                },
                friendly_response=f"Generating a 5-second cinematic motion sequence with {motion.replace('_', ' ')}.",
                executed_action=True,
            ).model_dump()

        # 5. Magic Erase Intent
        if any(w in transcript for w in ("erase", "remove object", "clean up", "inpaint", "brush")):
            return NLPCommandResponse(
                recognized_intent="magic_erase",
                confidence=0.90,
                target_tool="eraser",
                parameters={"brush_size": 24},
                friendly_response="Activating AI magic eraser brush.",
                executed_action=True,
            ).model_dump()

        # 6. Upscale / Restore Intent
        if any(w in transcript for w in ("upscale", "4k", "8k", "super resolution", "enhance", "sharpen")):
            return NLPCommandResponse(
                recognized_intent="upscale",
                confidence=0.96,
                target_tool="upscaler",
                parameters={"scale_factor": 4},
                friendly_response="Upscaling to ultra-high resolution 4K with face restoration.",
                executed_action=True,
            ).model_dump()

        # 7. Export / Download Intent
        if any(w in transcript for w in ("export", "download", "save", "render")):
            return NLPCommandResponse(
                recognized_intent="export",
                confidence=0.95,
                target_tool="export_dialog",
                parameters={"format": "png", "quality": 100},
                friendly_response="Opening high-resolution export dialog.",
                executed_action=True,
            ).model_dump()

        # Default Fallback: General Prompt Search / AI generation
        text_content = request_data.get_text()
        return NLPCommandResponse(
            recognized_intent="scene_swap",
            confidence=0.85,
            target_tool="scene_swap",
            parameters={"prompt": text_content, "preset_id": "executive_penthouse"},
            friendly_response=f"Interpreting creative directive: '{text_content}'",
            executed_action=True,
        ).model_dump()

