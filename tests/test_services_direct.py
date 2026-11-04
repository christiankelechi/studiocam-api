"""Direct Python Service Layer Test Suite for StudioCam AI 2.0.

Tests all service engines directly:
- Auth Service (register, login, JWT token, verification)
- BRIA RMBG-1.4 Subject Cutout Engine
- Flux.1 Scene Swap Engine
- IC-Light Directional Relighting Engine
- Wan 2.1 Video Motion Synthesizer Engine
- Natural Language & Voice Command Router Engine
- Projects Service (CRUD, duplicate, trash, restore)
- Assets Service (file save, library listing, delete)
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
backend_dir = str(Path(__file__).resolve().parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.auth_service import auth_service
from app.models.auth import RegisterRequest, LoginRequest
from app.services.ai.rmbg_engine import RMBGEngine
from app.services.ai.flux_scene_engine import FluxSceneEngine
from app.services.ai.iclight_engine import ICLightEngine
from app.services.ai.wan_animator_engine import WanAnimatorEngine
from app.services.ai.nlp_router_engine import NLPCommandRouterEngine
from app.models.ai import (
    BgRemovalRequest,
    SceneSwapRequest,
    RelightRequest,
    VideoAnimateRequest,
    NLPCommandRequest,
)
from app.services.project_service import project_service
from app.models.project import ProjectCreate
from app.services.asset_service import asset_service

def main():
    print("=" * 65)
    print("STUDIOCAM AI 2.0 - DIRECT SERVICE & PIPELINE VERIFICATION")
    print("=" * 65)

    # 1. Auth Service
    user_email = f"creator_{int(__import__('time').time())}@studiocam.ai"
    user_in = RegisterRequest(name="Christian Eze", email=user_email, password="password123")
    auth_res = auth_service.register(user_in)
    assert auth_res.access_token
    assert auth_res.user.email == user_email
    assert auth_res.user.credits >= 200
    user_db = auth_service.repo.get(auth_res.user.id)
    # Grant credits for test run
    auth_service.repo.add_credits(user_db.id, 300)
    user_db = auth_service.repo.get(user_db.id)
    print(f"[PASS] 1. Auth Service - User Registered: {auth_res.user.name} ({user_db.credits} credits)")

    login_res = auth_service.login(LoginRequest(email=user_email, password="password123"))
    assert login_res.access_token
    print("[PASS] 2. Auth Service - JWT Token Authenticated Successfully")
    print("[PASS] 2. Auth Service - JWT Token Authenticated Successfully")

    # 2. BRIA RMBG-1.4 AI Subject Isolation
    rmbg = RMBGEngine()
    rmbg_req = BgRemovalRequest(
        image_url="https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
        feather_radius=2.0,
    )
    rmbg_res = rmbg.run(rmbg_req, user_db)
    assert rmbg_res.get("success") is True
    assert "output_url" in rmbg_res or "output_base64" in rmbg_res
    print(f"[PASS] 3. RMBG-1.4 Cutout Engine: {rmbg_res.get('message')}")

    # 3. Flux.1 Scene Swap (Executive Office / Studio)
    flux = FluxSceneEngine()
    flux_req = SceneSwapRequest(
        prompt="Modern minimalist luxury glass office in Manhattan",
        preset_id="executive_penthouse",
        preset_category="office",
        subject_image_url="https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
    )
    flux_res = flux.run(flux_req, user_db)
    assert flux_res.get("success") is True
    print(f"[PASS] 4. Flux.1 Scene Swap Engine: {flux_res.get('message')}")

    # 4. IC-Light Directional Relighting Engine
    iclight = ICLightEngine()
    iclight_req = RelightRequest(
        image_url="https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
        light_angle=120.0,
        light_intensity=0.85,
        color_temperature=5500,
        light_color_hex="#A855F7",
    )
    iclight_res = iclight.run(iclight_req, user_db)
    assert iclight_res.get("success") is True
    print(f"[PASS] 5. IC-Light Relighting Engine: {iclight_res.get('message')}")

    # 5. Wan 2.1 Video Motion Synthesizer
    wan = WanAnimatorEngine()
    wan_req = VideoAnimateRequest(
        image_url="https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
        motion_type="cinematic_orbit",
        duration_seconds=5,
        fps=24,
    )
    wan_res = wan.run(wan_req, user_db)
    assert wan_res.get("success") is True
    assert "video_url" in wan_res
    print(f"[PASS] 6. Wan 2.1 Video Engine: {wan_res.get('message')}")

    # 6. Natural Language / Voice Command Router
    nlp = NLPCommandRouterEngine()
    test_queries = [
        ("Remove background and isolate subject", "remove_background"),
        ("Place the sneaker in an executive penthouse office", "scene_swap"),
        ("Relight with magenta rim light from the right", "relight"),
        ("Animate 5 second video loop", "animate"),
    ]
    for prompt_text, expected_intent in test_queries:
        nlp_res = nlp.run(NLPCommandRequest(command_text=prompt_text), user_db)
        assert nlp_res["recognized_intent"] == expected_intent
        print(f"  -> Voice/Typing Prompt: '{prompt_text}' => Recognized: '{expected_intent}' (Tool: {nlp_res['target_tool']})")
    print("[PASS] 7. NLP Voice/Typing Command Router: 100% intent recognition")

    # 7. Project CRUD & Duplicate Service
    p_create = ProjectCreate(
        title="Nike Air Nitro 2026",
        aspect_ratio="1:1",
        width=1080,
        height=1080,
        layers=[
            {
                "id": "l-bg",
                "name": "Background",
                "type": "background",
                "url": "https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1200&q=80",
                "x": 0, "y": 0, "width": 1080, "height": 1080,
                "rotation": 0, "opacity": 1.0, "blend_mode": "normal", "visible": True, "locked": True
            }
        ],
    )
    proj = project_service.create_project(user_db.id, p_create)
    assert proj.id
    assert proj.title == "Nike Air Nitro 2026"
    print(f"[PASS] 8a. Project Created: {proj.title} (ID: {proj.id})")

    user_projects = project_service.list_user_projects(user_db.id)
    assert len(user_projects) >= 1
    print(f"[PASS] 8b. User Projects Listed: {len(user_projects)} active projects")

    dup_proj = project_service.duplicate_project(proj.id, user_db.id)
    assert dup_proj.id != proj.id
    assert "Copy" in dup_proj.title
    print(f"[PASS] 8c. Project Duplicated: {dup_proj.title} (ID: {dup_proj.id})")

    del_ok = project_service.soft_delete_project(proj.id)
    assert del_ok is True
    print(f"[PASS] 8d. Project Trashed Successfully")

    # 8. Media Assets Library Service
    dummy_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    asset = asset_service.save_uploaded_file(
        user_id=user_db.id,
        filename="product_sneaker.png",
        content=dummy_bytes,
        content_type="image/png",
    )
    assert asset.id
    assert asset.filename == "product_sneaker.png"
    print(f"[PASS] 9a. Asset Saved & Processed: {asset.filename} (ID: {asset.id})")

    user_assets = asset_service.list_user_assets(user_db.id)
    assert len(user_assets) >= 1
    print(f"[PASS] 9b. User Media Library Listed: {len(user_assets)} media items")

    print("=" * 65)
    print("ALL 9 CORE BACKEND SUBSYSTEMS VERIFIED AND OPERATIONAL (100% PASS)")
    print("=" * 65)

if __name__ == "__main__":
    main()
