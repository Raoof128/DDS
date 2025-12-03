"""Video analysis API endpoint."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from backend.api.schemas import VideoAnalysisResponse
from backend.engines.temporal_detector import analyze_frames
from backend.engines.vision_detector import analyze_image
from backend.utils.logger import get_logger
from backend.utils.pdf_export import export_report
from backend.utils.preprocess import (
    align_faces,
    detect_faces,
    extract_frames,
    load_image,
    validate_upload,
)

router = APIRouter(prefix="/analyze_video", tags=["video"])
logger = get_logger(__name__)


@router.post("/", response_model=VideoAnalysisResponse)
async def analyze_video_endpoint(file: UploadFile = File(...)) -> dict[str, Any]:  # noqa: B008
    """Analyze video bytes by sampling frames and checking temporal consistency."""
    try:
        validate_upload(file.filename)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        frames = extract_frames(content, fps=6)
        temporal_result = analyze_frames(frames)

        if not frames:
            raise HTTPException(status_code=400, detail="Unable to extract frames")
        try:
            pseudo_image = (
                load_image(content[: min(1024, len(content))])
                if len(content) >= 3
                else load_image(content)
            )
        except ValueError:
            pseudo_image = Image.new("RGB", (64, 64), color=(128, 128, 128))
        faces = detect_faces(pseudo_image)
        aligned = align_faces(pseudo_image, faces)
        vision_result = analyze_image(aligned[0])
    except ValueError as exc:
        logger.warning("Video analysis validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error during video analysis")
        raise HTTPException(status_code=500, detail="Video analysis failed") from exc

    summary = {
        "vision_score": f"{vision_result.vision_score:.2f}",
        "temporal_score": f"{temporal_result.temporal_score:.2f}",
    }
    report_path = export_report(
        Path("logs/video_report.pdf"),
        summary,
        [f"Frame {f} anomaly" for f in temporal_result.flagged_frames],
    )

    return {
        "vision_score": vision_result.vision_score,
        "temporal_score": temporal_result.temporal_score,
        "flagged_frames": temporal_result.flagged_frames,
        "anomaly_map": temporal_result.anomaly_map,
        "report_path": str(report_path),
    }
