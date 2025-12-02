# API Reference

This document summarizes the Deepfake Detection System endpoints exposed via FastAPI with minimal examples.

## Health
- **GET `/health`**
  - Returns service status.
  - Response: `{ "status": "ok" }`

## Image Analysis
- **POST `/analyze_image/`**
  - Multipart form field: `file` (image/png, image/jpeg)
  - Example:
    ```bash
    curl -X POST http://localhost:8000/analyze_image/ \
      -F "file=@sample.png"
    ```
  - Response fields:
    - `vision_score` (float)
    - `artifact_heatmap_shape` (tuple)
    - `metadata_score` (float)
    - `metadata_anomalies` (list of strings)
    - `report_path` (string)

## Video Analysis
- **POST `/analyze_video/`**
  - Multipart form field: `file` (video bytes)
  - Example:
    ```bash
    curl -X POST http://localhost:8000/analyze_video/ \
      -F "file=@sample.mp4"
    ```
  - Response fields:
    - `vision_score`
    - `temporal_score`
    - `flagged_frames` (indices with anomalies)
    - `anomaly_map` (frame-to-frame differences)
    - `report_path`

## Audio Analysis
- **POST `/analyze_audio/`**
  - Multipart form field: `file` (audio/wav)
  - Example:
    ```bash
    curl -X POST http://localhost:8000/analyze_audio/ \
      -F "file=@sample.wav"
    ```
  - Response fields:
    - `audio_score`
    - `anomalies` (list)

## Multimodal Analysis
- **POST `/analyze_multimodal/`**
  - Optional multipart form fields: `image`, `video`, `audio`
  - At least one modality is required; vision is mandatory for fusion.
  - Example:
    ```bash
    curl -X POST http://localhost:8000/analyze_multimodal/ \
      -F "image=@sample.png" -F "audio=@sample.wav"
    ```
  - Response fields:
    - `deepfake_score` (float 0–100)
    - `classification` (REAL, UNCERTAIN, FAKE)
    - `confidence` (0–1)
    - `risk_level` (Low, Medium, High, Critical)
    - `components` (individual scores)

## Error Codes
- `400` – invalid payload (missing files, empty content, unsupported extension).
- `500` – unexpected server error (logged with context only, not payload bytes).

## Usage Notes
- Filenames are validated to block executable extensions.
- Uploaded bytes are processed in-memory; no external network calls are made.
- PDF reports are stored under `logs/` for auditability.
