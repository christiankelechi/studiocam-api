"""FastAPI Main Application Entry Point."""

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


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-converting browser-based AI studio backend orchestrator powering BRIA RMBG-1.4, Flux.1, IC-Light, and Wan 2.1 pipelines.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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

# Static file serving for uploads & generated output images
app.mount("/api/v1/uploads", StaticFiles(directory=settings.UPLOADS_PATH), name="uploads")
app.mount("/api/v1/outputs", StaticFiles(directory=settings.OUTPUTS_PATH), name="outputs")

# Include API v1 Routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Root health and discovery endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "api_v1": f"{settings.API_V1_STR}",
        "docs": "/docs",
    }

