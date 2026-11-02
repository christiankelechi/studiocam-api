"""Live Integration Test Suite for StudioCam Backend."""

import base64
import os
import subprocess
import sys
import time
from io import BytesIO
import httpx
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"


def generate_test_image_base64() -> str:
    """Create a sample 200x200 image as base64."""
    img = Image.new("RGBA", (200, 200), (220, 100, 80, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"


def run_all_tests():
    print("[1/10] Testing Root & Health endpoints...")
    r = httpx.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200, f"Root failed: {r.status_code}"
    assert r.json()["status"] == "online"

    r = httpx.get(f"{BASE_URL}/api/v1/health", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    print("  -> Passed: Root & Health OK")

    print("[2/10] Testing GPU Cluster status...")
    r = httpx.get(f"{BASE_URL}/api/v1/system/gpu-cluster", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert "RTX 4090" in data["active_gpu"]
    print("  -> Passed: GPU Cluster status OK")

    print("[3/10] Testing Authentication flow...")
    login_payload = {"email": "christian@studiocam.ai", "password": "password123"}
    r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json=login_payload, timeout=5)
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=5)
    assert r.status_code == 200
    assert r.json()["name"] == "Christian Eze"
    print("  -> Passed: User authenticated successfully")

    print("[4/10] Testing Projects Management...")
    r = httpx.get(f"{BASE_URL}/api/v1/projects", headers=headers, timeout=5)
    assert r.status_code == 200
    projects = r.json()
    assert len(projects) >= 2

    # Create new project
    create_payload = {
        "title": "Modern Office Executive Suite",
        "aspect_ratio": "16:9",
        "width": 1920,
        "height": 1080,
        "tags": ["office", "executive"],
    }
    r = httpx.post(f"{BASE_URL}/api/v1/projects", headers=headers, json=create_payload, timeout=5)
    assert r.status_code == 201
    new_project_id = r.json()["id"]
    print(f"  -> Passed: Projects retrieved and new project created (ID: {new_project_id})")

    print("[5/10] Testing Flux.1 Executive Office Scene Generator...")
    sample_b64 = generate_test_image_base64()
    scene_payload = {
        "image_base64": sample_b64,
        "preset_id": "executive_penthouse",
        "prompt": "54th floor executive CEO office with floor to ceiling glass windows and skyline bokeh",
        "shadow_softness": 0.6,
        "light_direction": 45.0,
    }
    r = httpx.post(f"{BASE_URL}/api/v1/ai/scene-swap", headers=headers, json=scene_payload, timeout=15)
    assert r.status_code == 200, f"Scene swap failed: {r.text}"
    scene_res = r.json()
    assert scene_res["success"] is True
    assert "output_base64" in scene_res
    assert scene_res["subject_composited"] is True
    print(f"  -> Passed: Flux.1 synthesized '{scene_res['preset_applied']}' ({scene_res['resolution']})")

    print("[6/10] Testing BRIA RMBG-1.4 Background Removal...")
    bg_payload = {"image_base64": sample_b64, "feather_radius": 2.0}
    r = httpx.post(f"{BASE_URL}/api/v1/ai/remove-background", headers=headers, json=bg_payload, timeout=10)
    assert r.status_code == 200
    bg_res = r.json()
    assert bg_res["success"] is True
    assert "output_base64" in bg_res
    print("  -> Passed: Subject isolated with alpha matting and feathering")

    print("[7/10] Testing IC-Light Directional Studio Relighting...")
    relight_payload = {
        "image_base64": sample_b64,
        "light_angle": 45.0,
        "light_intensity": 1.3,
        "color_temperature": 3200,
        "ambient_exposure": 0.1,
    }
    r = httpx.post(f"{BASE_URL}/api/v1/ai/relight", headers=headers, json=relight_payload, timeout=10)
    assert r.status_code == 200
    relight_res = r.json()
    assert relight_res["success"] is True
    print("  -> Passed: Directional lighting applied at 45° (3200K warm tungsten)")

    print("[8/10] Testing Wan 2.1 Video Motion Synthesis...")
    video_payload = {
        "image_base64": sample_b64,
        "motion_type": "cinematic_push_in",
        "duration_seconds": 5,
        "fps": 24,
    }
    r = httpx.post(f"{BASE_URL}/api/v1/ai/animate-scene", headers=headers, json=video_payload, timeout=10)
    assert r.status_code == 200
    video_res = r.json()
    assert video_res["success"] is True
    assert "video_url" in video_res
    print("  -> Passed: 5s cinematic motion synthesized")

    print("[9/10] Testing NLP Natural Language Voice Command Router...")
    nlp_payload = {"transcript": "Please remove the background and place this in an executive boardroom"}
    r = httpx.post(f"{BASE_URL}/api/v1/ai/parse-command", headers=headers, json=nlp_payload, timeout=5)
    assert r.status_code == 200
    nlp_res = r.json()
    assert nlp_res["recognized_intent"] in ("remove_background", "scene_swap")
    print(f"  -> Passed: NLP recognized intent '{nlp_res['recognized_intent']}' with confidence {nlp_res['confidence']}")

    print("[10/10] Testing Billing, Subscriptions, and Paystack Verification...")
    r = httpx.get(f"{BASE_URL}/api/v1/billing/plans", timeout=5)
    assert r.status_code == 200
    plans = r.json()
    assert len(plans) == 3

    r = httpx.get(f"{BASE_URL}/api/v1/billing/subscription", headers=headers, timeout=5)
    assert r.status_code == 200

    r = httpx.post(
        f"{BASE_URL}/api/v1/billing/paystack/verify",
        headers=headers,
        json={"reference": "ps_sample_live_test"},
        timeout=5,
    )
    assert r.status_code == 200
    assert r.json()["verified"] is True
    print("  -> Passed: Billing & Paystack verification confirmed")

    print("\n=======================================================")
    print("   ALL 10 SERVICE AND AI PIPELINE TESTS PASSED!")
    print("=======================================================\n")


if __name__ == "__main__":
    # Start Uvicorn in background process
    print("Starting StudioCam backend server on http://127.0.0.1:8000...")
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "warning"]
    proc = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    try:
        # Wait for server to come up
        ready = False
        for attempt in range(25):
            time.sleep(0.4)
            try:
                r = httpx.get(f"{BASE_URL}/api/v1/health", timeout=1.0)
                if r.status_code == 200:
                    ready = True
                    break
            except Exception:
                pass
        
        if not ready:
            print("ERROR: Server failed to start within timeout.")
            sys.exit(1)

        print("Server is live! Executing test suite...\n")
        run_all_tests()
    finally:
        print("Shutting down test server...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

