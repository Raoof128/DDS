"""Image analysis API endpoint."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.api.schemas import ImageAnalysisResponse
from backend.engines.metadata_analyzer import analyze_image_metadata
from backend.engines.vision_detector import analyze_image
from backend.utils.logger import get_logger
from backend.utils.pdf_export import export_report
from backend.utils.preprocess import align_faces, detect_faces, load_image, validate_upload

router = APIRouter(prefix="/analyze_image", tags=["image"])
logger = get_logger(__name__)


@router.post("/", response_model=ImageAnalysisResponse)
async def analyze_image_endpoint(file: UploadFile = File(...)) -> dict[str, Any]:  # noqa: B008
    """Analyze a single image for deepfake indicators."""
    try:
        validate_upload(file.filename)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        image = load_image(content)
        faces = detect_faces(image)
        aligned = align_faces(image, faces)
        vision_result = analyze_image(aligned[0])
        metadata_result = analyze_image_metadata(image)
    except ValueError as exc:
        logger.warning("Image analysis validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error during image analysis")
        raise HTTPException(status_code=500, detail="Image analysis failed") from exc

    summary = {
        "vision_score": f"{vision_result.vision_score:.2f}",
        "metadata_score": f"{metadata_result.metadata_score:.2f}",
    }
    report_path = export_report(Path("logs/image_report.pdf"), summary, metadata_result.anomalies)

    return {
        "vision_score": vision_result.vision_score,
        "artifact_heatmap_shape": vision_result.artifact_heatmap.shape,
        "metadata_score": metadata_result.metadata_score,
        "metadata_anomalies": metadata_result.anomalies,
        "report_path": str(report_path),
    }
