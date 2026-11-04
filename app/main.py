"""FastAPI Main Application Entry Point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

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
    description="High-converting browser-based AI studio backend orchestrator powering StudioCam Smart Cutout™, StudioCam UltraScene™, StudioCam CinemaLight™, and StudioCam CinemaMotion™ pipelines.",
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


# =========================================================================
# Standardized Error Handlers (Format: {"error": "<message>", ...})
# =========================================================================

@app.exception_handler(StudioException)
async def studio_exception_handler(request: Request, exc: StudioException):
    """Custom domain exception handler returning standard 'error' key."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "success": False,
            "error_type": exc.__class__.__name__,
            "extra": exc.details,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP Exception handler returning 'error' key instead of FastAPI's default 'detail'."""
    error_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_msg,
            "success": False,
            "status_code": exc.status_code,
        },
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation exception handler returning readable 'error' key with validation details."""
    errors = exc.errors()
    if errors:
        first = errors[0]
        field = " -> ".join(str(loc) for loc in first.get("loc", []) if loc != "body")
        msg = first.get("msg", "Invalid value")
        error_msg = f"Invalid field '{field}': {msg}" if field else f"Validation error: {msg}"
    else:
        error_msg = "Invalid request payload format."

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": error_msg,
            "success": False,
            "details": errors,
            "status_code": 422,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled exception handler returning standard 'error' key."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": str(exc) or "An unexpected server error occurred.",
            "success": False,
            "status_code": 500,
        },
    )


# Static file serving for uploads & generated output images (safe on serverless)
try:
    os.makedirs(settings.UPLOADS_PATH, exist_ok=True)
    os.makedirs(settings.OUTPUTS_PATH, exist_ok=True)
    app.mount("/api/v1/uploads", StaticFiles(directory=settings.UPLOADS_PATH), name="uploads")
    app.mount("/api/v1/outputs", StaticFiles(directory=settings.OUTPUTS_PATH), name="outputs")
    app.mount("/outputs", StaticFiles(directory=settings.OUTPUTS_PATH), name="outputs_direct")
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
        "message": "StudioCam AI Core Orchestrator is online and operational.",
        "platform": "Vercel Serverless Function" if is_serverless else "Local Python Host",
        "api_v1": f"{settings.API_V1_STR}",
        "docs": "/docs",
    }

