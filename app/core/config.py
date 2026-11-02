"""Application configuration and settings."""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Ensure directories exist
for directory in (DATA_DIR, UPLOADS_DIR, OUTPUTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    """Core application settings following 12-factor principles."""

    # Server Configuration
    PROJECT_NAME: str = "StudioCam AI Core Orchestrator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://cyberswitchapp-services.duckdns.org",
        "*",
    ]

    # Security & JWT Auth
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "studiocam-super-secure-production-jwt-secret-key-2026-v2"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Storage Paths
    STATIC_STORAGE_PATH: str = str(DATA_DIR)
    UPLOADS_PATH: str = str(UPLOADS_DIR)
    OUTPUTS_PATH: str = str(OUTPUTS_DIR)

    # Cloud AI GPU & Model Pipelines
    COMFYUI_URL: str = os.getenv("COMFYUI_URL", "http://localhost:8188")
    RUNPOD_GPU_URL: str = os.getenv("RUNPOD_GPU_URL", "")
    MOCK_GPU_PROCESSING: bool = os.getenv("MOCK_GPU_PROCESSING", "true").lower() == "true"

    # Payment Gateways (Paystack & Stripe)
    PAYSTACK_SECRET_KEY: str = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_paystack_studiocam_sample")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_stripe_studiocam_sample")


# Singleton settings instance
settings = Settings()

