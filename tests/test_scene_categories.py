"""Test Scene Generation for Office, Gym, Restaurant, and Lifestyle with Subject Upload.
"""

import json
import urllib.request
from PIL import Image
from io import BytesIO
import base64

BASE_URL = "http://127.0.0.1:8000"

def create_sample_subject_base64():
    # Create a simple portrait/subject image (red jacket person)
    img = Image.new("RGBA", (300, 450), (0, 0, 0, 0))
    for x in range(80, 220):
        for y in range(50, 400):
            img.putpixel((x, y), (220, 60, 60, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def post(path, data):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def test():
    print("==================================================")
    print("Testing Scene Generation: Office, Gym, Restaurant, Lifestyle")
    print("==================================================")
    subject_b64 = create_sample_subject_base64()

    # 1. Office Scene
    payload_office = {
        "preset_id": "executive_penthouse",
        "image_base64": subject_b64,
        "prompt": "Luxury CEO corner office with panoramic city skyline at sunset"
    }
    s, r = post("/api/v1/ai/scene-swap", payload_office)
    print(f"1. Office Scene -> HTTP {s}, Composited: {r.get('subject_composited')}, Preset: {r.get('preset_applied')}")
    assert s == 200 and r.get("subject_composited") is True

    # 2. Gym Scene
    payload_gym = {
        "preset_id": "luxury_equinox_gym",
        "image_base64": subject_b64,
        "prompt": "Ultra-luxury modern fitness club with dumbbells and moody lighting"
    }
    s, r = post("/api/v1/ai/scene-swap", payload_gym)
    print(f"2. Gym Scene -> HTTP {s}, Composited: {r.get('subject_composited')}, Category: {r.get('category')}")
    assert s == 200 and r.get("subject_composited") is True

    # 3. Restaurant Scene
    payload_restaurant = {
        "preset_id": "michelin_fine_dining",
        "image_base64": subject_b64,
        "prompt": "Michelin 3-star fine dining restaurant with candlelight and wine glasses"
    }
    s, r = post("/api/v1/ai/scene-swap", payload_restaurant)
    print(f"3. Restaurant Scene -> HTTP {s}, Composited: {r.get('subject_composited')}, Category: {r.get('category')}")
    assert s == 200 and r.get("subject_composited") is True

    # 4. Custom Scene Prompt (e.g. "I am in a gym")
    payload_custom = {
        "prompt": "I am working out at a high-tech modern gym with neon lighting",
        "image_base64": subject_b64
    }
    s, r = post("/api/v1/ai/scene-swap", payload_custom)
    print(f"4. Custom Scene Prompt -> HTTP {s}, Composited: {r.get('subject_composited')}, Output URL: {bool(r.get('output_url'))}")
    assert s == 200 and r.get("subject_composited") is True

    print("==================================================")
    print("ALL SCENE CREATION & SUBJECT COMPOSITING TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test()

