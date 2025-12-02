# Architecture & Design Overview

## Goals
- Provide a modular, educational deepfake detection demo with safe heuristics.
- Keep all processing local with no external lookups or biometric storage.
- Enable easy swapping of detectors and future model upgrades.

## Components
1. **Ingestion & Preprocessing** (`backend/utils/preprocess.py`): validation, frame extraction, face alignment, MFCC calculation.
2. **Vision Detector** (`backend/engines/vision_detector.py`): texture/lighting heuristics + artifact heatmap.
3. **Temporal Consistency** (`backend/engines/temporal_detector.py`): frame-to-frame anomaly scoring.
4. **Audio Detector** (`backend/engines/audio_detector.py`): MFCC variance and drift analysis (simulated).
5. **Metadata Analyzer** (`backend/engines/metadata_analyzer.py`): EXIF parsing and spoof checks.
6. **Fusion Engine** (`backend/engines/fusion_engine.py`): weighted blend with risk buckets and confidence.
7. **API** (`backend/api/*`): FastAPI routers per modality plus multimodal fusion.
8. **Dashboard** (`frontend/*`): simple HTML/JS to submit files and display results.
9. **Reporting** (`backend/utils/pdf_export.py`): PDF summary of scores and anomalies.

## Data Flow
1. User uploads media from the dashboard.
2. API validates filenames and loads bytes.
3. Preprocessing normalizes inputs; video bytes are chunked into mock frames.
4. Modal detectors compute scores and anomaly lists.
5. Fusion engine blends scores into a `deepfake_score`, classification, risk, and confidence.
6. PDF report is generated and stored in `logs/`.
7. Dashboard renders scores, risk level, and JSON explainability payload.

## Security & Privacy Considerations
- Disallows executable uploads via extension checks.
- No external network calls; all processing is local.
- Logging avoids sensitive payload details.
- Designed for synthetic or user-provided content only.

## Extending the System
- Replace heuristics with ONNX/TFLite models in the engines.
- Swap mock frame extraction with `opencv-python` or `ffmpeg-python`.
- Integrate real MFCC extraction via `librosa` and face detectors via `mediapipe`.
- Update `FusionResult` weights and risk buckets to match empirical thresholds.
