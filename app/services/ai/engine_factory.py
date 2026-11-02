"""AI Engine Factory implementing the Factory Pattern."""

from typing import Dict, Type
from app.services.ai.base_engine import BaseAIEngine
from app.services.ai.flux_scene_engine import FluxSceneEngine
from app.services.ai.iclight_engine import ICLightEngine
from app.services.ai.nlp_router_engine import NLPCommandRouterEngine
from app.services.ai.rmbg_engine import RMBGEngine
from app.services.ai.wan_animator_engine import WanAnimatorEngine


class AIEngineFactory:
    """Factory to retrieve appropriate AI engine instance."""

    _registry: Dict[str, BaseAIEngine] = {
        "rmbg": RMBGEngine(),
        "flux_scene": FluxSceneEngine(),
        "iclight": ICLightEngine(),
        "wan_animator": WanAnimatorEngine(),
        "nlp_router": NLPCommandRouterEngine(),
    }

    @classmethod
    def get_engine(cls, engine_type: str) -> BaseAIEngine:
        engine = cls._registry.get(engine_type)
        if not engine:
            raise ValueError(f"Unknown AI engine type: '{engine_type}'")
        return engine


# Global factory accessor
ai_factory = AIEngineFactory

