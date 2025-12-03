# Threat Model & Risk Assessment

## Scope
- Educational deepfake detection demo with local-only processing.
- Inputs: user-uploaded images, short videos, and audio clips.
- Outputs: heuristic scores, risk labels, and PDF reports stored under `logs/`.

## Assets
- Uploaded media bytes (synthetic or user-provided)
- Generated reports
- Logs and operational metrics
- Detection heuristics and configuration

## Threats & Mitigations
| Threat | Likelihood | Impact | Mitigations |
| --- | --- | --- | --- |
| Malicious file uploads (executables, scripts) | Medium | Medium | `validate_upload` blocks risky extensions; FastAPI size limits configurable; run behind WAF/reverse proxy. |
| Model/logic misuse for surveillance | Low | High | Documentation emphasizes educational use, synthetic data only, and no biometric persistence. |
| Information leakage via logs | Medium | Medium | Logging avoids payload contents; focuses on metadata. |
| Dependency vulnerabilities | Medium | Medium | Pinned requirements, CI lint/type/test, periodic updates. |
| Denial of service via large payloads | Medium | Medium | Lightweight processing, configurable limits at gateway, extraction loops guarded with validations. |
| Report leakage | Low | Medium | Reports stored locally; recommend access controls and rotation (see SECURITY.md). |

## Assumptions
- Environment enforces TLS and authentication when exposed publicly.
- Only synthetic or user-consented data is processed.
- No external network calls from detectors.

## Security Controls Checklist
- [x] Upload validation and MIME gating at endpoints
- [x] Input size sanity checks in preprocessors
- [x] Structured logging without sensitive content
- [x] Static frontend served from FastAPI for tight coupling
- [x] CI lint/type/test gates
- [x] Dockerized runtime for reproducibility

## Residual Risks
- Heuristic detectors may yield false positives/negatives; clearly documented limitations.
- Client-side uploads are not authenticated by default; deploy behind auth for production contexts.

## Recommendations
- Add request ID propagation for traceability.
- Configure rate limiting at ingress.
- Periodically review dependencies with vulnerability scanners (e.g., `pip-audit`).
