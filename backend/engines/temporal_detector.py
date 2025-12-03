"""Temporal consistency checker for video frames."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TemporalResult:
    """Result of temporal consistency analysis."""

    temporal_score: float
    flagged_frames: list[int]
    anomaly_map: list[float]


def analyze_frames(frames: list[NDArray[np.float32]]) -> TemporalResult:
    """Analyze temporal consistency using frame-to-frame differences."""
    if not frames:
        return TemporalResult(temporal_score=0.0, flagged_frames=[], anomaly_map=[])

    anomalies: list[float] = []
    flagged: list[int] = []
    for idx in range(1, len(frames)):
        prev, curr = frames[idx - 1], frames[idx]
        min_shape = tuple(min(p, c) for p, c in zip(prev.shape, curr.shape, strict=False))
        prev = prev[: min_shape[0], : min_shape[1]]
        curr = curr[: min_shape[0], : min_shape[1]]
        diff = float(np.mean(np.abs(prev - curr)))
        anomalies.append(diff)
        if diff > 25:
            flagged.append(idx)
    avg_anomaly = float(np.mean(anomalies)) if anomalies else 0.0
    temporal_score = float(max(0.0, 100.0 - avg_anomaly))
    logger.info("Temporal analysis complete with score %.2f", temporal_score)
    return TemporalResult(
        temporal_score=temporal_score,
        flagged_frames=flagged,
        anomaly_map=anomalies,
    )
