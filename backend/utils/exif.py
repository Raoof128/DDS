"""Utilities to extract EXIF metadata from images."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from PIL import ExifTags, Image

from .logger import get_logger

logger = get_logger(__name__)


def _safe_getexif(image: Image.Image) -> Mapping[int, Any]:
    getter: Callable[[], Mapping[int, Any] | None] | None = getattr(image, "_getexif", None)
    if getter is None:
        return {}
    exif = getter()
    return exif or {}


def extract_exif(image: Image.Image) -> dict[str, str]:
    """Extract EXIF metadata into a dictionary with readable keys."""
    logger.debug("Extracting EXIF metadata")
    exif_data: dict[str, str] = {}
    try:
        raw_exif = _safe_getexif(image)
        for key, value in raw_exif.items():
            name = ExifTags.TAGS.get(key, str(key))
            exif_data[name] = str(value)
    except Exception as exc:  # pragma: no cover - depends on Pillow internals
        logger.warning("Unable to read EXIF: %s", exc)
    logger.info("Found %d EXIF fields", len(exif_data))
    return exif_data
