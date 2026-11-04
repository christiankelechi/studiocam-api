"""Live Integration Test Suite for StudioCam Backend."""

import base64
import os
import subprocess
import sys
import time
from io import BytesIO
import httpx
from PIL import Image

BASE_URL = "http://127.0.0.1:8008"


def generate_test_image_base64() -> str:
    """Create a sample 200x200 image as base64."""
    img = Image.new("RGBA", (200, 200), (220, 100, 80, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"


def run_all_tests():
    print("[1/11] Testing Root & Health endpoints...")
    r = httpx.get(f"{BASE_URL}/", timeout=5)
    assert r.status_code == 200, f"Root failed: {r.status_code}"
    assert r.json()["status"] == "online"
    assert "message" in r.json()

    r = httpx.get(f"{BASE_URL}/api/v1/health", timeout=5)
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    assert "message" in r.json()
    print("  -> Passed: Root & Health OK with success message")

    print("[2/11] Testing GPU Cluster status...")
    r = httpx.get(f"{BASE_URL}/api/v1/system/gpu-cluster", timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert "message" in data
    assert "RTX 4090" in data["active_gpu"]
    print("  -> Passed: GPU Cluster status OK with message")

    print("[3/11] Testing Authentication flow & Success message format...")
    login_payload = {"email": "christian@studiocam.ai", "password": "password123"}
    r = httpx.post(f"{BASE_URL}/api/v1/auth/login", json=login_payload, timeout=5)
    assert r.status_code == 200, f"Login failed: {r.text}"
    login_data = r.json()
    assert login_data["access_token"] is not None
    assert "message" in login_data, "Expected key 'message' in success response"
    token = login_data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=5)
    assert r.status_code == 200
    assert r.json()["name"] == "Christian Eze"
    print(f"  -> Passed: Authenticated with message '{login_data['message']}'")

    print("[4/11] Testing Standardized Error Handling with key 'error'...")
    # Test 4.1: Invalid credentials error (401)
    bad_login = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={"email": "wrong@studiocam.ai", "password": "bad"}, timeout=5)
    assert bad_login.status_code == 401
    bad_login_data = bad_login.json()
    assert "error" in bad_login_data, f"Expected key 'error' in error response, got: {bad_login_data}"
    assert "detail" not in bad_login_data, "Legacy 'detail' key should be replaced by 'error'"
    print(f"  -> Passed: 401 error returned key 'error' ('{bad_login_data['error']}')")

    # Test 4.2: Missing route 404 error
    not_found_res = httpx.get(f"{BASE_URL}/api/v1/does-not-exist-route", timeout=5)
    assert not_found_res.status_code == 404
    not_found_data = not_found_res.json()
    assert "error" in not_found_data, f"Expected key 'error' on 404, got: {not_found_data}"
    assert "detail" not in not_found_data, "Legacy 'detail' key should be replaced by 'error'"
    print(f"  -> Passed: 404 error returned key 'error' ('{not_found_data['error']}')")

    # Test 4.3: Request validation 422 error
    bad_val_res = httpx.post(f"{BASE_URL}/api/v1/ai/remove-background", headers=headers, json={"invalid_field": 123}, timeout=5)
    # Background removal requires image_base64 or image_url
    assert bad_val_res.status_code in (400, 422, 500)
    bad_val_data = bad_val_res.json()
    assert "error" in bad_val_data, f"Expected key 'error' on validation/pipeline error, got: {bad_val_data}"
    print(f"  -> Passed: Validation/Pipeline error returned key 'error' ('{bad_val_data['error']}')")

    # Test 4.4: Domain ResourceNotFoundError (404)
    missing_proj = httpx.get(f"{BASE_URL}/api/v1/projects/non_existent_project_999", headers=headers, timeout=5)
    assert missing_proj.status_code == 404
    missing_proj_data = missing_proj.json()
    assert "error" in missing_proj_data, f"Expected key 'error' on domain 404, got: {missing_proj_data}"
    print(f"  -> Passed: Domain 404 returned key 'error' ('{missing_proj_data['error']}')")

    print("[5/11] Testing Projects Management & Success Messages...")
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
    created_proj = r.json()
    assert "message" in created_proj
    new_project_id = created_proj["id"]
    print(f"  -> Passed: Project created with message '{created_proj['message']}' (ID: {new_project_id})")

    print("[6/11] Testing Flux.1 Executive Office Scene Generator...")
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
    assert "message" in scene_res
    assert "output_base64" in scene_res
    assert scene_res["subject_composited"] is True
    print(f"  -> Passed: Flux.1 synthesized with message '{scene_res['message']}'")

    print("[7/11] Testing BRIA RMBG-1.4 Background Removal...")
    bg_payload = {"image_base64": sample_b64, "feather_radius": 2.0}
    r = httpx.post(f"{BASE_URL}/api/v1/ai/remove-background", headers=headers, json=bg_payload, timeout=10)
    assert r.status_code == 200
    bg_res = r.json()
    assert bg_res["success"] is True
    assert "message" in bg_res
    assert "output_base64" in bg_res
    print(f"  -> Passed: RMBG cutout completed with message '{bg_res['message']}'")

    print("[8/11] Testing IC-Light Directional Studio Relighting...")
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
    assert "message" in relight_res
    print(f"  -> Passed: Relighting applied with message '{relight_res['message']}'")

    print("[9/11] Testing Wan 2.1 Video Motion Synthesis...")
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
    assert "message" in video_res
    assert "video_url" in video_res
    print(f"  -> Passed: Video motion synthesized with message '{video_res['message']}'")

    print("[10/11] Testing NLP Natural Language Voice Command Router...")
    nlp_payload = {"transcript": "Please remove the background and place this in an executive boardroom"}
    r = httpx.post(f"{BASE_URL}/api/v1/ai/parse-command", headers=headers, json=nlp_payload, timeout=5)
    assert r.status_code == 200
    nlp_res = r.json()
    assert "message" in nlp_res
    assert nlp_res["recognized_intent"] in ("remove_background", "scene_swap")
    print(f"  -> Passed: NLP recognized intent with message '{nlp_res['message']}'")

    print("[11/11] Testing Billing, Subscriptions, and Paystack Verification...")
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
    paystack_res = r.json()
    assert paystack_res["verified"] is True
    assert "message" in paystack_res
    print(f"  -> Passed: Paystack verified with message '{paystack_res['message']}'")

    print("\n=======================================================")
    print("   ALL 10 SERVICE AND AI PIPELINE TESTS PASSED!")
    print("=======================================================\n")


if __name__ == "__main__":
    # Start Uvicorn in background process on dedicated test port 8008
    print("Starting StudioCam backend server on http://127.0.0.1:8008...", flush=True)
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8008", "--log-level", "warning"]
    proc = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    try:
        # Wait for server to come up
        ready = False
        for attempt in range(30):
            time.sleep(0.4)
            if proc.poll() is not None:
                print(f"ERROR: Server process exited early with code {proc.returncode}!", flush=True)
                sys.exit(1)
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

