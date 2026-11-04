"""Full Backend Integration Test Suite for StudioCam AI 2.0.

Tests every endpoint:
- Auth (register, login, me)
- AI Subject Isolation (BRIA RMBG-1.4)
- AI Scene & Office Swap (Flux.1)
- AI Studio Relighting (IC-Light)
- AI Video Motion (Wan 2.1)
- NLP Command Router (Voice/text intent classification)
- Projects CRUD & Duplicate
- Media Assets Library & Upload
- System Health & GPU Node status
"""

import sys
import io
import os
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
backend_dir = str(Path(__file__).resolve().parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("STARTING STUDIOCAM AI 2.0 BACKEND TEST SUITE")
    print("=" * 60)

    # 1. System Health
    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    health_data = r.json()
    assert health_data.get("status") == "healthy", f"Unexpected status: {health_data}"
    print("[PASS] 1. System Health OK:", health_data.get("status"))

    # 2. Auth - Register & Login
    test_email = f"test_creator_{int(__import__('time').time())}@studiocam.ai"
    reg_payload = {"name": "Test Creator", "email": test_email, "password": "password123"}
    r = client.post("/api/v1/auth/register", json=reg_payload)
    assert r.status_code in [200, 201], f"Register failed: {r.text}"
    reg_data = r.json()
    token = reg_data.get("access_token")
    assert token, "No access token in registration response"
    print("[PASS] 2. User Registration OK. Token acquired.")

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Auth - Get Profile
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200, f"Get profile failed: {r.text}"
    user_info = r.json()
    assert user_info.get("email") == test_email
    print("[PASS] 3. Auth Profile /me OK:", user_info.get("name"), f"({user_info.get('credits')} credits)")

    # 4. AI - BRIA RMBG-1.4 Subject Isolation (remove-background)
    bg_payload = {
        "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
        "feather_radius": 2.0,
    }
    r = client.post("/api/v1/ai/remove-background", json=bg_payload, headers=headers)
    assert r.status_code == 200, f"RMBG-1.4 failed: {r.text}"
    bg_data = r.json()
    assert bg_data.get("success") is True, f"RMBG returned failure: {bg_data}"
    assert "output_url" in bg_data or "output_base64" in bg_data
    print("[PASS] 4. BRIA RMBG-1.4 Subject Isolation OK:", bg_data.get("message"))

    # 5. AI - Flux.1 Scene Swap (Executive Office / Studio)
    scene_payload = {
        "prompt": "Modern luxury high-rise penthouse office overlooking Tokyo skyline",
        "preset_id": "executive_penthouse",
        "preset_category": "office",
        "subject_image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
    }
    r = client.post("/api/v1/ai/scene-swap", json=scene_payload, headers=headers)
    assert r.status_code == 200, f"Flux.1 Scene Swap failed: {r.text}"
    scene_data = r.json()
    assert scene_data.get("success") is True
    print("[PASS] 5. Flux.1 Scene Swap OK:", scene_data.get("message"))

    # 6. AI - IC-Light Directional Relighting
    relight_payload = {
        "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
        "light_angle": 120.0,
        "light_intensity": 0.85,
        "color_temperature": 5500,
        "light_color_hex": "#A855F7",
    }
    r = client.post("/api/v1/ai/relight", json=relight_payload, headers=headers)
    assert r.status_code == 200, f"IC-Light failed: {r.text}"
    relight_data = r.json()
    assert relight_data.get("success") is True
    print("[PASS] 6. IC-Light Directional Relighting OK:", relight_data.get("message"))

    # 7. AI - Wan 2.1 Video Motion Synthesis
    video_payload = {
        "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
        "motion_type": "orbit_360",
        "duration_seconds": 5,
        "motion_prompt": "Cinematic camera arc orbit",
    }
    r = client.post("/api/v1/ai/animate-scene", json=video_payload, headers=headers)
    assert r.status_code == 200, f"Wan 2.1 failed: {r.text}"
    video_data = r.json()
    assert video_data.get("success") is True
    print("[PASS] 7. Wan 2.1 Video Motion OK:", video_data.get("message"))

    # 8. AI - Natural Language Voice & Typing NLP Command Router
    nlp_commands = [
        ("Remove background from the sneaker", "remove_background"),
        ("Change background to a modern tech office in Manhattan", "swap_scene"),
        ("Relight the product from the left with warm light", "relight"),
        ("Animate 5 second video loop", "animate_video"),
    ]
    for text, expected_intent in nlp_commands:
        r = client.post("/api/v1/ai/parse-command", json={"command_text": text}, headers=headers)
        assert r.status_code == 200, f"NLP command failed for '{text}': {r.text}"
        nlp_data = r.json()
        assert nlp_data.get("recognized_intent") == expected_intent, f"Wrong intent for '{text}': {nlp_data}"
        print(f"  -> NLP Command '{text}' recognized as '{expected_intent}' with confidence {nlp_data.get('confidence')}")
    print("[PASS] 8. NLP Voice/Typing Command Router OK for all intents.")

    # 9. Projects - Create, List, Duplicate, Delete
    proj_payload = {
        "title": "Summer Sneaker Campaign",
        "aspect_ratio": "1:1",
        "width": 1080,
        "height": 1080,
        "layers": [
            {
                "id": "l-1",
                "name": "Product Layer",
                "type": "image",
                "url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=800&q=80",
                "x": 200, "y": 200, "width": 600, "height": 600,
                "rotation": 0, "opacity": 1.0, "blend_mode": "normal", "visible": True, "locked": False
            }
        ]
    }
    r = client.post("/api/v1/projects", json=proj_payload, headers=headers)
    assert r.status_code in [200, 201], f"Create project failed: {r.text}"
    proj_data = r.json()
    proj_id = proj_data.get("id")
    assert proj_id, "Project ID missing"
    print(f"[PASS] 9a. Project Created OK (ID: {proj_id}, Title: {proj_data.get('title')})")

    # List Projects
    r = client.get("/api/v1/projects", headers=headers)
    assert r.status_code == 200
    user_projects = r.json()
    assert any(p.get("id") == proj_id for p in user_projects), "Created project not in user list"
    print(f"[PASS] 9b. List Projects OK ({len(user_projects)} projects found)")

    # Duplicate Project
    r = client.post(f"/api/v1/projects/{proj_id}/duplicate", headers=headers)
    assert r.status_code == 200
    dup_data = r.json()
    assert dup_data.get("id") != proj_id
    print(f"[PASS] 9c. Duplicate Project OK (New ID: {dup_data.get('id')})")

    # Delete Project
    r = client.delete(f"/api/v1/projects/{proj_id}", headers=headers)
    assert r.status_code == 200
    print("[PASS] 9d. Delete Project OK.")

    # 10. Media Assets - Upload & List
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    files = {"file": ("test_upload.png", io.BytesIO(fake_png), "image/png")}
    r = client.post("/api/v1/assets/upload", files=files, headers=headers)
    assert r.status_code in [200, 201], f"Asset upload failed: {r.text}"
    asset_res = r.json()
    asset_obj = asset_res.get("asset", {})
    asset_id = asset_obj.get("id")
    print(f"[PASS] 10a. Asset Upload OK (ID: {asset_id}, Name: {asset_obj.get('filename')})")

    r = client.get("/api/v1/assets", headers=headers)
    assert r.status_code == 200
    assets_list = r.json()
    assert any(a.get("id") == asset_id for a in assets_list), "Uploaded asset not in list"
    print(f"[PASS] 10b. List Assets OK ({len(assets_list)} assets in user library)")

    print("=" * 60)
    print("ALL 10 TEST SUITES PASSED FLAWLESSLY (100% SUCCESS)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

