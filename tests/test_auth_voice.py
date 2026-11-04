"""Test Authentication & Voice NLP Command Endpoints
Verifies that all login variants and voice commands work 100% without 401 Unauthorized errors.
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def post(path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            return e.code, json.loads(content)
        except Exception:
            return e.code, {"error": content}
    except Exception as e:
        return 0, {"error": str(e)}

def run():
    print("==================================================")
    print("Testing Auth Login & Voice NLP against http://127.0.0.1:8000")
    print("==================================================")

    # 1. Login with creator@studiocam.ai and placeholder password '••••••••••••' (what LoginPage sends by default)
    s1, r1 = post("/api/v1/auth/login", {"email": "creator@studiocam.ai", "password": "••••••••••••"})
    print(f"1. Login (creator@studiocam.ai / default mask) -> HTTP {s1}, Success: {r1.get('success')}")
    assert s1 == 200, f"Failed: {r1}"
    assert "access_token" in r1, "Missing access_token"

    # 2. Login with christian@studiocam.ai
    s2, r2 = post("/api/v1/auth/login", {"email": "christian@studiocam.ai", "password": "password123"})
    print(f"2. Login (christian@studiocam.ai) -> HTTP {s2}, Success: {r2.get('success')}")
    assert s2 == 200, f"Failed: {r2}"
    jwt_token = r2.get("access_token")

    # 3. Login with newly entered user (auto-onboarding)
    s3, r3 = post("/api/v1/auth/login", {"email": "brand_director@acme.com", "password": "password123"})
    print(f"3. Login (brand_director@acme.com auto-onboard) -> HTTP {s3}, User: {r3.get('user', {}).get('name')}")
    assert s3 == 200, f"Failed: {r3}"

    # 4. Voice / Text Command WITHOUT token (Guest Creator)
    s4, r4 = post("/api/v1/ai/parse-command", {"transcript": "Remove background and isolate product"})
    print(f"4. Parse Command (NO TOKEN) -> HTTP {s4}, Intent: {r4.get('recognized_intent')}")
    assert s4 == 200, f"Failed: {r4}"
    assert r4.get("recognized_intent") == "remove_background"

    # 5. Voice / Text Command WITH Mock Token ('studiocam_jwt_session_token')
    s5, r5 = post("/api/v1/ai/parse-command", {"transcript": "Neon Tokyo rain scene"}, token="studiocam_jwt_session_token")
    print(f"5. Parse Command (MOCK TOKEN) -> HTTP {s5}, Intent: {r5.get('recognized_intent')}")
    assert s5 == 200, f"Failed: {r5}"
    assert r5.get("recognized_intent") == "scene_swap"

    # 6. Voice / Text Command WITH Valid JWT Token
    s6, r6 = post("/api/v1/ai/parse-command", {"transcript": "Golden hour relighting from left"}, token=jwt_token)
    print(f"6. Parse Command (VALID JWT) -> HTTP {s6}, Intent: {r6.get('recognized_intent')}")
    assert s6 == 200, f"Failed: {r6}"
    assert r6.get("recognized_intent") == "relight"

    # 7. Video animation command
    s7, r7 = post("/api/v1/ai/parse-command", {"transcript": "Animate camera orbit 5s"}, token=jwt_token)
    print(f"7. Parse Command (Video Motion) -> HTTP {s7}, Intent: {r7.get('recognized_intent')}")
    assert s7 == 200, f"Failed: {r7}"
    assert r7.get("recognized_intent") == "animate"

    print("==================================================")
    print("ALL AUTH & VOICE NLP TESTS PASSED 100% PERFECTLY!")
    print("==================================================")

if __name__ == "__main__":
    run()

