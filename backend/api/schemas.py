"""Pydantic schemas for API responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ImageAnalysisResponse(BaseModel):
    """Schema for image analysis outputs."""

    vision_score: float = Field(..., ge=0, le=100)
    artifact_heatmap_shape: tuple[int, ...]
    metadata_score: float = Field(..., ge=0, le=100)
    metadata_anomalies: list[str]
    report_path: str


class VideoAnalysisResponse(BaseModel):
    """Schema for video analysis outputs."""

    vision_score: float = Field(..., ge=0, le=100)
    temporal_score: float = Field(..., ge=0, le=100)
    flagged_frames: list[int]
    anomaly_map: list[float]
    report_path: str


class AudioAnalysisResponse(BaseModel):
    """Schema for audio analysis outputs."""

    audio_score: float = Field(..., ge=0, le=100)
    anomalies: list[str]


class MultimodalResponse(BaseModel):
    """Schema for fusion outputs."""

    deepfake_score: float = Field(..., ge=0, le=100)
    classification: str
    confidence: float = Field(..., ge=0, le=1)
    risk_level: str
    components: dict[str, float]
