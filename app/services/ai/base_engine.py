"""Abstract Base AI Engine implementing the Template Method Pattern."""

from abc import ABC, abstractmethod
import base64
from io import BytesIO
from typing import Any, Dict, Optional, Tuple
from PIL import Image

from app.core.exceptions import AIPipelineError, InsufficientCreditsError
from app.models.auth import UserInDB
from app.repositories.user_repository import user_repository


class BaseAIEngine(ABC):
    """
    Abstract Base Class for all AI pipeline engines.
    Employs the Template Method Pattern to standardize processing steps:
    1. Validation
    2. Credit Check
    3. Pipeline Execution
    4. Post-processing & Persistence
    5. Credit Deduction
    """

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Name of the AI engine (e.g., BRIA RMBG-1.4, Flux.1)."""
        pass

    @property
    @abstractmethod
    def credit_cost(self) -> int:
        """Credit cost for running this pipeline operation."""
        pass

    def run(self, request_data: Any, user: UserInDB) -> Dict[str, Any]:
        """Template method governing execution flow."""
        # Step 1: Input Validation
        self.validate_input(request_data)

        # Step 2: Credit Check
        if user.credits < self.credit_cost:
            raise InsufficientCreditsError(required=self.credit_cost, available=user.credits)

        # Step 3: Execute core AI pipeline
        result = self.execute_pipeline(request_data, user)

        # Step 4: Deduct credits on successful completion
        remaining_credits = user_repository.deduct_credits(user.id, self.credit_cost)
        result["remaining_credits"] = remaining_credits
        result["credits_used"] = self.credit_cost
        result["engine"] = self.engine_name

        return result

    @abstractmethod
    def validate_input(self, request_data: Any) -> None:
        """Validate pipeline-specific request parameters."""
        pass

    @abstractmethod
    def execute_pipeline(self, request_data: Any, user: UserInDB) -> Dict[str, Any]:
        """Core AI pipeline execution logic (implemented by concrete subclasses)."""
        pass

    # Reusable Image Helpers for Concrete Engines
    @staticmethod
    def load_image_from_base64_or_bytes(base64_str: str) -> Image.Image:
        """Decode base64 data URI or raw base64 string into a PIL Image."""
        try:
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]
            image_data = base64.b64decode(base64_str)
            image = Image.open(BytesIO(image_data))
            return image.convert("RGBA")
        except Exception as e:
            raise AIPipelineError("ImageLoader", f"Failed to decode base64 image: {str(e)}")

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """Encode PIL Image to a base64 data URI string."""
        buffered = BytesIO()
        image.save(buffered, format=format)
        encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
        mime = "image/png" if format.upper() == "PNG" else "image/jpeg"
        return f"data:{mime};base64,{encoded}"

