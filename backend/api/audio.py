"""Audio analysis API endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.api.schemas import AudioAnalysisResponse
from backend.engines.audio_detector import analyze_audio
from backend.utils.logger import get_logger
from backend.utils.preprocess import validate_upload

router = APIRouter(prefix="/analyze_audio", tags=["audio"])
logger = get_logger(__name__)


@router.post("/", response_model=AudioAnalysisResponse)
async def analyze_audio_endpoint(file: UploadFile = File(...)) -> dict[str, Any]:  # noqa: B008
    """Analyze audio files for deepfake indicators (simulated)."""
    try:
        validate_upload(file.filename)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        result = analyze_audio(content)
    except ValueError as exc:
        logger.warning("Audio analysis validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error during audio analysis")
        raise HTTPException(status_code=500, detail="Audio analysis failed") from exc

    return {"audio_score": result.audio_score, "anomalies": result.anomalies}
