"""FastAPI Main Application Entry Point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api_router import api_router
from app.core.config import settings
from app.core.exceptions import StudioException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle events."""
    print("[INFO] StudioCam AI Backend Server Initialized.")
    print(f"[INFO] API documentation available at: http://localhost:{settings.PORT}/docs")
    yield
    print("[INFO] StudioCam AI Backend Server Shutting down.")


# On Vercel serverless functions, avoid lifespan event issues
is_serverless = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-converting browser-based AI studio backend orchestrator powering BRIA RMBG-1.4, Flux.1, IC-Light, and Wan 2.1 pipelines.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=None if is_serverless else lifespan,
    redirect_slashes=False,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for domain errors
@app.exception_handler(StudioException)
async def studio_exception_handler(request: Request, exc: StudioException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__, "extra": exc.details},
    )

# Static file serving for uploads & generated output images (safe on serverless)
try:
    if os.path.exists(settings.UPLOADS_PATH):
        app.mount("/api/v1/uploads", StaticFiles(directory=settings.UPLOADS_PATH), name="uploads")
    if os.path.exists(settings.OUTPUTS_PATH):
        app.mount("/api/v1/outputs", StaticFiles(directory=settings.OUTPUTS_PATH), name="outputs")
except Exception:
    pass

# Include API v1 Routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
@app.get("/api")
@app.get("/api/index")
def root():
    """Root health and discovery endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "platform": "Vercel Serverless Function" if is_serverless else "Local Python Host",
        "api_v1": f"{settings.API_V1_STR}",
        "docs": "/docs",
    }

