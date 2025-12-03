"""Preprocessing utilities for image, video, and audio inputs."""

from __future__ import annotations

import io
import wave

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from .logger import get_logger

logger = get_logger(__name__)


def load_image(file_bytes: bytes) -> Image.Image:
    """Load image from raw bytes with safety checks."""
    logger.debug("Loading image from bytes")
    if not file_bytes:
        raise ValueError("No image content provided")
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        logger.info("Image loaded with size %s", image.size)
        return image
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to load image: %s", exc)
        raise ValueError("Invalid image file") from exc


def extract_frames(file_bytes: bytes, fps: int = 5) -> list[NDArray[np.float32]]:
    """Mock frame extraction from a video stream."""
    logger.debug("Extracting frames at %s fps", fps)
    if fps <= 0:
        raise ValueError("fps must be positive")
    if not file_bytes:
        raise ValueError("No video content provided")
    chunk_size = max(1, len(file_bytes) // max(1, fps))
    frames: list[NDArray[np.float32]] = []
    for idx in range(0, len(file_bytes), chunk_size):
        chunk = file_bytes[idx : idx + chunk_size]
        arr: NDArray[np.float32] = np.frombuffer(chunk, dtype=np.uint8)
        side = int(np.sqrt(len(arr))) or 1
        frame: NDArray[np.float32] = np.resize(arr, (side, side)).astype(np.float32)
        frames.append(frame)
    logger.info("Extracted %d frames", len(frames))
    return frames


def detect_faces(image: Image.Image) -> list[tuple[int, int, int, int]]:
    """Mock face detection returning center crop bounding boxes."""
    width, height = image.size
    bbox = (
        int(width * 0.25),
        int(height * 0.25),
        int(width * 0.75),
        int(height * 0.75),
    )
    logger.debug("Detected face bbox: %s", bbox)
    return [bbox]


def align_faces(image: Image.Image, faces: list[tuple[int, int, int, int]]) -> list[Image.Image]:
    """Return cropped face regions for downstream processing."""
    if not faces:
        logger.warning("No faces provided for alignment; returning full image")
        return [image]
    aligned = [image.crop(face) for face in faces]
    logger.info("Aligned %d faces", len(aligned))
    return aligned


def extract_mfcc(audio_bytes: bytes, sample_rate: int = 16000) -> NDArray[np.float_]:
    """Simulate MFCC extraction using simple FFT-based features."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    if not audio_bytes:
        logger.warning("Empty audio payload; returning zeroed MFCC")
        return np.zeros((1, 13), dtype=np.float_)
    if len(audio_bytes) % 2:
        audio_bytes += b"\x00"
    audio_signal: NDArray[np.int16] = np.frombuffer(audio_bytes, dtype=np.int16)
    if audio_signal.size == 0:
        return np.zeros((1, 13), dtype=np.float_)
    spectrum: NDArray[np.float_] = np.abs(np.fft.rfft(audio_signal))
    bins = np.array_split(spectrum, 13)
    mfcc = np.array([np.mean(bin_) if bin_.size else 0.0 for bin_ in bins], dtype=np.float_)
    logger.debug("MFCC shape: %s", mfcc.shape)
    return mfcc.reshape(1, -1)


def parse_wav(audio_bytes: bytes) -> tuple[NDArray[np.int16], int]:
    """Parse WAV bytes into numpy array and sample rate."""
    if not audio_bytes:
        raise ValueError("No audio content provided")
    with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())
    audio_array: NDArray[np.int16] = np.frombuffer(frames, dtype=np.int16)
    logger.info("Parsed WAV with %d samples at %d Hz", audio_array.size, sample_rate)
    return audio_array, sample_rate


def batch_frames(
    frames: list[NDArray[np.float32]], batch_size: int = 8
) -> list[list[NDArray[np.float32]]]:
    """Group frames into temporal batches for analysis."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    batches = [frames[i : i + batch_size] for i in range(0, len(frames), batch_size)]
    logger.debug("Created %d frame batches", len(batches))
    return batches


def normalize_image(image: Image.Image) -> NDArray[np.float32]:
    """Normalize image pixels to [0, 1]."""
    array = np.asarray(image).astype(np.float32) / 255.0
    logger.debug("Normalized image shape: %s", array.shape)
    return array


def validate_upload(filename: str | None) -> None:
    """Basic validation to prevent suspicious uploads."""
    if not filename:
        raise ValueError("Filename is required")
    blocked_extensions = {".exe", ".dll", ".bat"}
    if any(filename.lower().endswith(ext) for ext in blocked_extensions):
        logger.warning("Blocked file upload attempt: %s", filename)
        raise ValueError("Unsupported file type")
