"""Vercel Serverless Function Entrypoint for StudioCam AI FastAPI Backend."""

import os
import sys

# Ensure backend root directory is on sys.path across all deployment shapes
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

for path in (current_dir, parent_dir, os.getcwd(), "/var/task", "/var/task/backend"):
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

try:
    from app.main import app
except Exception as e:
    # Diagnostic fallback: If initialization fails during cold start,
    # capture the full traceback and return it as JSON instead of crashing with 500 FUNCTION_INVOCATION_FAILED.
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    err_traceback = traceback.format_exc()
    app = FastAPI(title="StudioCam Initialization Diagnostic Handler")

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    def diagnostic_error_handler(full_path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Backend cold-start initialization failed on Vercel",
                "message": str(e),
                "traceback": err_traceback.splitlines(),
                "sys_path": sys.path,
                "current_dir": current_dir,
                "parent_dir": parent_dir,
                "cwd": os.getcwd(),
            },
        )

# Export app for Vercel ASGI runtime
__all__ = ["app"]
