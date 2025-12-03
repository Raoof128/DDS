"""Unit tests for detector engines and utilities."""

from __future__ import annotations

import numpy as np

from backend.engines.audio_detector import analyze_audio
from backend.engines.fusion_engine import fuse_results
from backend.engines.metadata_analyzer import MetadataResult
from backend.engines.temporal_detector import TemporalResult
from backend.engines.vision_detector import VisionResult
from backend.utils.preprocess import extract_frames, extract_mfcc, validate_upload


def test_extract_frames_requires_content() -> None:
    try:
        extract_frames(b"", fps=1)
    except ValueError as exc:
        assert "No video content" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for empty content")


def test_validate_upload_blocks_executables() -> None:
    try:
        validate_upload("malware.exe")
    except ValueError as exc:
        assert "Unsupported" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for blocked extension")


def test_fusion_risk_levels() -> None:
    fusion = fuse_results(
        VisionResult(vision_score=80, artifact_heatmap=np.zeros((2, 2)), details={}),
        TemporalResult(temporal_score=60, flagged_frames=[], anomaly_map=[]),
        analyze_audio(b"1234"),
        MetadataResult(metadata_score=90, metadata={}, anomalies=[]),
    )
    assert fusion.deepfake_score >= 0
    assert fusion.classification in {"REAL", "UNCERTAIN", "FAKE"}
    assert fusion.risk_level in {"Low", "Medium", "High", "Critical"}


def test_extract_mfcc_handles_empty() -> None:
    mfcc = extract_mfcc(b"")
    assert mfcc.shape == (1, 13)


def test_vision_result_dataclass() -> None:
    vision = VisionResult(vision_score=10, artifact_heatmap=np.zeros((2, 2)), details={"a": 1})
    assert vision.details["a"] == 1
    assert vision.artifact_heatmap.shape == (2, 2)
