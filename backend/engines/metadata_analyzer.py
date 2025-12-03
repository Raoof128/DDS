"""Metadata and forensic analyzer."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from backend.utils.exif import extract_exif
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetadataResult:
    """Result of EXIF and metadata checks."""

    metadata_score: float
    metadata: dict[str, str]
    anomalies: list[str]


def analyze_metadata(image_metadata: dict[str, str]) -> MetadataResult:
    """Inspect metadata for inconsistencies and editing traces."""
    anomalies: list[str] = []
    camera_model = image_metadata.get("Model")
    timestamp = image_metadata.get("DateTime")

    if not image_metadata:
        anomalies.append("Missing EXIF data may indicate export or editing")
    if camera_model and "mock" in camera_model.lower():
        anomalies.append("Camera model spoofing detected")
    if timestamp and "T" not in timestamp:
        anomalies.append("Non-standard timestamp format")

    score = max(0.0, 100.0 - len(anomalies) * 20)
    logger.info("Metadata analysis complete with score %.2f", score)
    return MetadataResult(metadata_score=score, metadata=image_metadata, anomalies=anomalies)


def analyze_image_metadata(image: Image.Image) -> MetadataResult:
    """Convenience wrapper to extract and analyze EXIF metadata."""
    metadata = extract_exif(image)
    return analyze_metadata(metadata)
