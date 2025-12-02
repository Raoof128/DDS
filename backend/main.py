"""FastAPI application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import audio, image, multimodal, video
from backend.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Deepfake Detection System", version="1.0.0")

app.include_router(image.router)
app.include_router(video.router)
app.include_router(audio.router)
app.include_router(multimodal.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/dashboard", StaticFiles(directory=str(frontend_path), html=True), name="dashboard")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    logger.info("Health check pinged")
    return {"status": "ok"}
