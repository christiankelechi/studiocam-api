"""Live Server E2E Verification Script.
Tests all endpoints against http://127.0.0.1:8000/
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def make_req(path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            return status, json.loads(content)
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            return e.code, json.loads(content)
        except Exception:
            return e.code, {"error": content}
    except Exception as e:
        return 0, {"error": str(e)}

def run_tests():
    print("==================================================")
    print("Testing StudioCam Live Backend at http://127.0.0.1:8000")
    print("==================================================")

    # 1. Health
    s, r = make_req("/api/v1/health")
    print(f"1. /api/v1/health -> Status {s}, OK: {r.get('status') == 'healthy'}")
    assert s == 200, f"Health check failed: {r}"

    # 2. System GPU Cluster
    s, r = make_req("/api/v1/system/gpu-cluster")
    print(f"2. /api/v1/system/gpu-cluster -> Status {s}, Workers: {len(r.get('workers', []))}")
    assert s == 200, f"GPU Cluster check failed: {r}"

    # 3. Auth Login with Seeded Demo User
    login_payload = {
        "email": "christian@studiocam.ai",
        "password": "password123"
    }
    s, r = make_req("/api/v1/auth/login", login_payload)
    print(f"3. /api/v1/auth/login -> Status {s}, Success: {r.get('success')}")
    assert s == 200, f"Login failed: {r}"
    token = r.get("access_token")

    # 4. Auth Me
    s, r = make_req("/api/v1/auth/me", token=token)
    print(f"4. /api/v1/auth/me -> Status {s}, User: {r.get('email')}")
    assert s == 200, f"Auth me failed: {r}"

    # 5. AI Background Remover
    bg_payload = {
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "feather_radius": 2
    }
    s, r = make_req("/api/v1/ai/remove-background", bg_payload, token=token)
    out = bool(r.get("output_url") or r.get("output_base64") or r.get("output_image_url"))
    print(f"5. /api/v1/ai/remove-background -> Status {s}, Output: {out}")
    assert s == 200, f"Remove background failed: {r}"

    # 6. AI Scene Swap
    scene_payload = {
        "subject_image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "prompt": "Luxury marble showroom table with soft morning sunlight",
        "preset_id": "luxury_marble"
    }
    s, r = make_req("/api/v1/ai/scene-swap", scene_payload, token=token)
    out = bool(r.get("output_url") or r.get("output_base64") or r.get("output_image_url"))
    print(f"6. /api/v1/ai/scene-swap -> Status {s}, Output: {out}")
    assert s == 200, f"Scene swap failed: {r}"

    # 7. AI Relight
    relight_payload = {
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "angle": 45,
        "intensity": 80,
        "color_temp": 5500,
        "color_hex": "#F59E0B"
    }
    s, r = make_req("/api/v1/ai/relight", relight_payload, token=token)
    out = bool(r.get("output_url") or r.get("output_base64") or r.get("output_image_url"))
    print(f"7. /api/v1/ai/relight -> Status {s}, Output: {out}")
    assert s == 200, f"Relight failed: {r}"

    # 8. AI Video Animation
    video_payload = {
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "prompt": "Slow cinematic camera orbit around subject",
        "motion_type": "orbit",
        "duration_seconds": 5
    }
    s, r = make_req("/api/v1/ai/animate-scene", video_payload, token=token)
    print(f"8. /api/v1/ai/animate-scene -> Status {s}, Video URL: {bool(r.get('video_url'))}")
    assert s == 200, f"Animate failed: {r}"

    # 9. AI Magic Erase
    erase_payload = {
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "mask_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }
    s, r = make_req("/api/v1/ai/magic-erase", erase_payload, token=token)
    out = bool(r.get("output_url") or r.get("output_base64") or r.get("output_image_url"))
    print(f"9. /api/v1/ai/magic-erase -> Status {s}, Output: {out}")
    assert s == 200, f"Magic erase failed: {r}"

    # 10. AI Parse Command (Voice & Typing router)
    cmd_payload = {
        "transcript": "Swap background to a sunny Tokyo rooftop",
        "confidence": 0.98
    }
    s, r = make_req("/api/v1/ai/parse-command", cmd_payload, token=token)
    intent = r.get("recognized_intent") or r.get("intent")
    print(f"10. /api/v1/ai/parse-command -> Status {s}, Intent: {intent}")
    assert s == 200, f"Parse command failed: {r}"

    # 11. Projects List
    s, r = make_req("/api/v1/projects", token=token)
    print(f"11. /api/v1/projects -> Status {s}, Count: {len(r)}")
    assert s == 200, f"Projects list failed: {r}"

    # 12. Billing Plans
    s, r = make_req("/api/v1/billing/plans")
    plans_count = len(r) if isinstance(r, list) else len(r.get('plans', []))
    print(f"12. /api/v1/billing/plans -> Status {s}, Plans: {plans_count}")
    assert s == 200, f"Billing plans failed: {r}"

    print("==================================================")
    print("ALL 12 LIVE BACKEND SUITES PASSED 100% PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
