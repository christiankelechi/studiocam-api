"""Application configuration and settings."""

import os
from pathlib import Path
import tempfile
from typing import List
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Automatically load environment variables from .env if present
try:
    from dotenv import load_dotenv
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except Exception:
    pass

# Safe writable storage directory for Vercel / AWS Lambda (never crash on read-only filesystem)
try:
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV") or os.getenv("VERCEL_REGION") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        DATA_DIR = Path(tempfile.gettempdir()) / "studiocam" / "data"
    else:
        DATA_DIR = BASE_DIR / "data"

    UPLOADS_DIR = DATA_DIR / "uploads"
    OUTPUTS_DIR = DATA_DIR / "outputs"

    for directory in (DATA_DIR, UPLOADS_DIR, OUTPUTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
except Exception:
    DATA_DIR = Path(tempfile.gettempdir())
    UPLOADS_DIR = DATA_DIR
    OUTPUTS_DIR = DATA_DIR


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
        "https://studiocam-api.vercel.app",
        "https://studiocam.vercel.app",
        "*",
    ]

    # Security & JWT Auth
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "7d85eaa5cfcd92e35b9cc2cdb6fe403de1153d04c14da43c82141214007e699b"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Storage Paths
    STATIC_STORAGE_PATH: str = str(DATA_DIR)
    UPLOADS_PATH: str = str(UPLOADS_DIR)
    OUTPUTS_PATH: str = str(OUTPUTS_DIR)

    # Cloud AI GPU & Model Pipelines (Hybrid Fallback Architecture)
    ENABLE_EXTERNAL_AI: bool = os.getenv("ENABLE_EXTERNAL_AI", "true").lower() == "true"
    POLLINATIONS_ENABLED: bool = os.getenv("POLLINATIONS_ENABLED", "true").lower() == "true"
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    COMFYUI_URL: str = os.getenv("COMFYUI_URL", "http://localhost:8188")
    RUNPOD_GPU_URL: str = os.getenv("RUNPOD_GPU_URL", "")
    RUNPOD_API_KEY: str = os.getenv("RUNPOD_API_KEY", "")
    MOCK_GPU_PROCESSING: bool = os.getenv("MOCK_GPU_PROCESSING", "false").lower() == "true"

    # FastAPI Public URL
    FASTAPI_URL: str = os.getenv("FASTAPI_URL", "https://studiocam-api.vercel.app/")

    # Payment Gateways (Paystack & Stripe)
    PAYSTACK_SECRET_KEY: str = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_paystack_studiocam_sample")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_stripe_studiocam_sample")


# Singleton settings instance
settings = Settings()

