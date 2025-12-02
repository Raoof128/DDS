"""Multimodal fusion engine to combine detector outputs."""

from __future__ import annotations

from dataclasses import dataclass

from backend.engines.audio_detector import AudioResult
from backend.engines.metadata_analyzer import MetadataResult
from backend.engines.temporal_detector import TemporalResult
from backend.engines.vision_detector import VisionResult
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FusionResult:
    """Aggregated fusion outcome."""

    deepfake_score: float
    classification: str
    confidence: float
    risk_level: str
    components: dict[str, float]


RISK_BUCKETS = [
    (0, 25, "Low"),
    (25, 50, "Medium"),
    (50, 75, "High"),
    (75, 101, "Critical"),
]


def fuse_results(
    vision: VisionResult,
    temporal: TemporalResult,
    audio: AudioResult,
    metadata: MetadataResult,
) -> FusionResult:
    """Blend component scores into a final deepfake score."""
    weights = {
        "vision": 0.4,
        "temporal": 0.2,
        "audio": 0.2,
        "metadata": 0.2,
    }
    composite = (
        vision.vision_score * weights["vision"]
        + temporal.temporal_score * weights["temporal"]
        + audio.audio_score * weights["audio"]
        + metadata.metadata_score * weights["metadata"]
    )
    deepfake_score = float(max(0.0, min(100.0, composite)))
    classification = (
        "REAL" if deepfake_score < 40 else "UNCERTAIN" if deepfake_score < 65 else "FAKE"
    )
    confidence = float(min(1.0, abs(deepfake_score - 50) / 50 + 0.2))
    risk_level = next(level for low, high, level in RISK_BUCKETS if low <= deepfake_score < high)
    logger.info(
        "Fusion produced score %.2f with classification %s and risk %s",
        deepfake_score,
        classification,
        risk_level,
    )
    return FusionResult(
        deepfake_score=deepfake_score,
        classification=classification,
        confidence=confidence,
        risk_level=risk_level,
        components={
            "vision_score": vision.vision_score,
            "temporal_score": temporal.temporal_score,
            "audio_score": audio.audio_score,
            "metadata_score": metadata.metadata_score,
        },
    )
