"""Multimodal analysis endpoint combining vision, audio, temporal, and metadata."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from backend.api.schemas import MultimodalResponse
from backend.engines.audio_detector import analyze_audio
from backend.engines.fusion_engine import fuse_results
from backend.engines.metadata_analyzer import analyze_image_metadata
from backend.engines.temporal_detector import analyze_frames
from backend.engines.vision_detector import analyze_image
from backend.utils.logger import get_logger
from backend.utils.preprocess import (
    align_faces,
    detect_faces,
    extract_frames,
    load_image,
    validate_upload,
)

router = APIRouter(prefix="/analyze_multimodal", tags=["multimodal"])
logger = get_logger(__name__)


@router.post("/", response_model=MultimodalResponse)
async def analyze_multimodal_endpoint(
    image: UploadFile | None = File(None),  # noqa: B008
    video: UploadFile | None = File(None),  # noqa: B008
    audio: UploadFile | None = File(None),  # noqa: B008
) -> dict[str, Any]:
    """Combine available modalities into a single decision."""
    if not any([image, video, audio]):
        raise HTTPException(status_code=400, detail="At least one modality required")

    try:
        vision_result = None
        metadata_result = None
        if image:
            validate_upload(image.filename)
            image_bytes = await image.read()
            img = load_image(image_bytes)
            faces = detect_faces(img)
            aligned = align_faces(img, faces)
            vision_result = analyze_image(aligned[0])
            metadata_result = analyze_image_metadata(img)

        temporal_result = None
        if video:
            validate_upload(video.filename)
            video_bytes = await video.read()
            frames = extract_frames(video_bytes)
            temporal_result = analyze_frames(frames)
            if not vision_result and frames:
                try:
                    pseudo_img = load_image(video_bytes[: min(1024, len(video_bytes))])
                except ValueError:
                    pseudo_img = Image.new("RGB", (64, 64), color=(128, 128, 128))
                vision_result = analyze_image(align_faces(pseudo_img, detect_faces(pseudo_img))[0])

        audio_result = None
        if audio:
            validate_upload(audio.filename)
            audio_bytes = await audio.read()
            audio_result = analyze_audio(audio_bytes)

        if vision_result is None:
            raise HTTPException(status_code=400, detail="Vision modality required for fusion")
        if temporal_result is None:
            temporal_result = analyze_frames([])
        if audio_result is None:
            audio_result = analyze_audio(b"0")
        if metadata_result is None:
            placeholder = Image.new("RGB", (32, 32), color=(128, 128, 128))
            metadata_result = analyze_image_metadata(placeholder)

    except ValueError as exc:
        logger.warning("Multimodal validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error during multimodal analysis")
        raise HTTPException(status_code=500, detail="Multimodal analysis failed") from exc

    fusion = fuse_results(vision_result, temporal_result, audio_result, metadata_result)
    return {
        "deepfake_score": fusion.deepfake_score,
        "classification": fusion.classification,
        "confidence": fusion.confidence,
        "risk_level": fusion.risk_level,
        "components": fusion.components,
    }
