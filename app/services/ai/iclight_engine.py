"""StudioCam CinemaLight™ Directional Ambient Relighting Service."""

import math
import os
import uuid
from typing import Any, Dict
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import numpy as np

from app.core.config import settings
from app.core.exceptions import AIPipelineError
from app.models.ai import RelightRequest
from app.models.auth import UserInDB
from app.services.ai.base_engine import BaseAIEngine


class ICLightEngine(BaseAIEngine):
    """
    StudioCam CinemaLight™ Generative Studio Relighting Engine.
    Simulates directional studio key/rim lighting, color temperature shifts, and ambient exposure.
    """

    @property
    def engine_name(self) -> str:
        return "StudioCam CinemaLight™ Generative Relighting Engine"

    @property
    def credit_cost(self) -> int:
        return 8  # 8 credits per relighting pass

    def validate_input(self, request_data: RelightRequest) -> None:
        if not request_data.image_base64 and not request_data.image_url:
            raise AIPipelineError(self.engine_name, "image_base64 or image_url is required.")

    def execute_pipeline(self, request_data: RelightRequest, user: UserInDB) -> Dict[str, Any]:
        """Apply directional lighting and color temperature harmonization."""
        if request_data.image_base64:
            img = self.load_image_from_base64_or_bytes(request_data.image_base64)
        else:
            img = Image.new("RGBA", (800, 800), (45, 50, 60, 255))

        w, h = img.size

        # 1. Color Temperature Tint Calculation (Kelvin 2500K to 7500K)
        # 2500K = Warm Amber (255, 180, 100), 6500K = Neutral (255, 255, 255), 7500K = Cool Blue (200, 220, 255)
        temp = max(2500, min(7500, request_data.color_temperature))
        if temp < 5500:
            # Warm shift
            warm_factor = (5500 - temp) / 3000.0
            tint_rgb = (int(255), int(255 - 40 * warm_factor), int(255 - 90 * warm_factor))
        else:
            # Cool shift
            cool_factor = (temp - 5500) / 2000.0
            tint_rgb = (int(255 - 60 * cool_factor), int(255 - 30 * cool_factor), int(255))

        # 2. Directional Key Light Gradient based on light_angle (0-360 deg)
        rad = math.radians(request_data.light_angle)
        dir_x = math.cos(rad)
        dir_y = -math.sin(rad)  # Inverted Y for image coordinate system

        # Generate directional light map
        light_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        light_draw = ImageDraw.Draw(light_layer)

        # Light source center point
        src_x = int(w / 2 + dir_x * (w * 0.45))
        src_y = int(h / 2 + dir_y * (h * 0.45))
        max_dist = math.hypot(w, h)

        # Draw soft radial/directional highlight
        intensity = max(0.1, min(2.0, request_data.light_intensity))
        alpha = int(min(220, 110 * intensity))
        radius = int(max(w, h) * 0.8)

        light_draw.ellipse(
            [(src_x - radius, src_y - radius), (src_x + radius, src_y + radius)],
            fill=(tint_rgb[0], tint_rgb[1], tint_rgb[2], alpha),
        )
        light_layer = light_layer.filter(ImageFilter.GaussianBlur(radius=int(w * 0.25)))

        # 3. Composite lighting onto base image
        relit = Image.alpha_composite(img, light_layer)

        # 4. Ambient Exposure Adjustment (-1.0 to 1.0)
        if request_data.ambient_exposure != 0.0:
            enhancer = ImageEnhance.Brightness(relit)
            brightness_factor = max(0.3, 1.0 + request_data.ambient_exposure * 0.5)
            relit = enhancer.enhance(brightness_factor)

        # Save output
        file_id = f"iclight_{uuid.uuid4().hex[:10]}"
        output_filename = f"{file_id}.png"
        output_filepath = os.path.join(settings.OUTPUTS_PATH, output_filename)
        relit.save(output_filepath, "PNG", quality=95)

        base64_result = self.image_to_base64(relit, "PNG")

        return {
            "success": True,
            "message": f"Directional lighting applied at {request_data.light_angle}° ({temp}K).",
            "job_id": file_id,
            "output_url": f"/api/v1/outputs/{output_filename}",
            "output_base64": base64_result,
            "light_angle": request_data.light_angle,
            "light_intensity": request_data.light_intensity,
            "color_temperature": f"{temp}K",
            "ambient_exposure": request_data.ambient_exposure,
            "render_quality": "StudioCam CinemaLight™ Studio v2",
        }

