"""Audio deepfake detection (simulated)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from backend.utils.logger import get_logger
from backend.utils.preprocess import extract_mfcc

logger = get_logger(__name__)


@dataclass
class AudioResult:
    """Result of audio analysis."""

    audio_score: float
    anomalies: list[str]


def analyze_audio(audio_bytes: bytes) -> AudioResult:
    """Analyze audio by inspecting MFCC distribution and synthetic cues."""
    mfcc = extract_mfcc(audio_bytes)
    variance = float(np.var(mfcc))
    drift = float(np.max(mfcc) - np.min(mfcc)) if mfcc.size else 0.0
    score = float(max(0.0, 100.0 - (variance * 10 + drift * 0.001)))
    anomalies: list[str] = []
    if variance < 1.0:
        anomalies.append("Flat MFCC distribution suggests synthetic speech")
    if drift > 5000:
        anomalies.append("High spectral drift may indicate voice cloning artifacts")
    logger.info("Audio analysis complete with score %.2f", score)
    return AudioResult(audio_score=score, anomalies=anomalies)
