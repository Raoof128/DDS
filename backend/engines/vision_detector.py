"""Vision-based deepfake detection engine."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from backend.utils.heatmap import generate_mock_heatmap
from backend.utils.logger import get_logger
from backend.utils.preprocess import normalize_image

logger = get_logger(__name__)


@dataclass
class VisionResult:
    """Result of vision detector."""

    vision_score: float
    artifact_heatmap: NDArray[np.float_]
    details: dict[str, float]


def _compute_texture_score(image_array: NDArray[np.float32]) -> float:
    """Compute a mock skin texture anomaly score based on local variance."""
    variance = float(np.var(image_array))
    score = min(100.0, variance * 1000)
    logger.debug("Texture variance %.4f -> score %.2f", variance, score)
    return score


def _compute_lighting_score(image_array: NDArray[np.float32]) -> float:
    """Compute simple lighting consistency score using channel balance."""
    channel_means = np.mean(image_array, axis=(0, 1))
    balance = float(np.std(channel_means))
    score = max(0.0, 100.0 - balance * 300)
    logger.debug("Lighting balance %.4f -> score %.2f", balance, score)
    return score


def analyze_image(image: Image.Image) -> VisionResult:
    """Analyze an image for deepfake artifacts using lightweight heuristics."""
    array = normalize_image(image)
    texture_score = _compute_texture_score(array)
    lighting_score = _compute_lighting_score(array)
    vision_score = float(np.clip((texture_score * 0.6 + lighting_score * 0.4), 0, 100))
    heatmap = generate_mock_heatmap(*image.size)
    details = {
        "texture_anomaly": texture_score,
        "lighting_consistency": lighting_score,
        "skin_texture_anomaly": max(0.0, 100 - texture_score / 2),
        "gan_fingerprint": float(np.mean(array) * 50),
    }
    logger.info("Vision analysis complete with score %.2f", vision_score)
    return VisionResult(vision_score=vision_score, artifact_heatmap=heatmap, details=details)
