# Operations, Deployment, and Maintenance

This guide summarizes how to run, test, and deploy the Deepfake Detection System (DFS) in a production-like environment.

## Local Development
- Install dependencies: `make install`
- Run the API with auto-reload: `make run`
- Execute quality gates: `make lint && make typecheck && make test`
- Clean generated artifacts: `make clean`

## Docker
- Build the image: `make docker-build`
- Run the container: `make docker-run`
- The service listens on port `8000`; open `http://localhost:8000/dashboard` for the dashboard.

## Configuration & Logging
- Logging is configured in `backend/utils/logger.py`; customize levels via `configure_logging` in `backend/main.py`.
- Reports are stored under `logs/`; avoid committing generated PDFs. Use `make clean` to remove them.

## Security & Privacy Hygiene
- Accept **only synthetic or user-provided** samples.
- Block executable uploads and validate file extensions using `validate_upload` in `backend/utils/preprocess.py`.
- Keep dependencies patched: upgrade `requirements*.txt` regularly.
- Avoid sending media to external services; all processing is local.

## Health & Monitoring
- Health probe: `GET /health`
- Operational logs: stdout or file handler configured in `backend/utils/logger.py`.

## Testing & QA
- Unit tests: `pytest`
- Lint: `ruff check .`
- Formatting check: `black --check .`
- Type checks: `mypy backend`

## Deployment Notes
- For production, run Uvicorn/Gunicorn behind a reverse proxy (e.g., Nginx) and enforce TLS termination.
- Set resource limits for container deployments to prevent runaway workloads.
- Rotate and restrict access to logs and reports; consider mounting a persistent volume if retention is required.
