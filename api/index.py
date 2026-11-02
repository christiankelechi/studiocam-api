"""Vercel Serverless Function Entrypoint for StudioCam AI FastAPI Backend."""

import os
import sys

# Ensure backend root directory is on sys.path across all deployment shapes
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Direct top-level import of FastAPI app
from app.main import app

# Explicit top-level aliases required by Vercel Python runtime
application = app
handler = app
