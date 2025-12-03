"""API tests using FastAPI TestClient."""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backend.main import app  # noqa: E402

client = TestClient(app)


def _sample_image_bytes() -> bytes:
    img = Image.fromarray(np.full((16, 16, 3), 128, dtype=np.uint8))
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_image_analysis() -> None:
    files = {"file": ("test.png", _sample_image_bytes(), "image/png")}
    response = client.post("/analyze_image/", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert "vision_score" in payload
    assert "metadata_score" in payload


def test_audio_analysis_defaults() -> None:
    files = {"file": ("test.wav", b"\x00\x01\x02\x03", "audio/wav")}
    response = client.post("/analyze_audio/", files=files)
    assert response.status_code == 200
    assert "audio_score" in response.json()


def test_video_analysis() -> None:
    video_bytes = bytes([i % 256 for i in range(2048)])
    files = {"file": ("test.mp4", video_bytes, "video/mp4")}
    response = client.post("/analyze_video/", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["temporal_score"] >= 0
    assert isinstance(payload["flagged_frames"], list)


def test_multimodal_success_with_image_only() -> None:
    files = {"image": ("test.png", _sample_image_bytes(), "image/png")}
    response = client.post("/analyze_multimodal/", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"] in {"REAL", "UNCERTAIN", "FAKE"}
    assert set(payload["components"].keys()) == {
        "vision_score",
        "temporal_score",
        "audio_score",
        "metadata_score",
    }


def test_multimodal_requires_modality() -> None:
    response = client.post("/analyze_multimodal/")
    assert response.status_code == 400
