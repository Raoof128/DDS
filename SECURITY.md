# Security Policy

## Supported Versions
- Main branch is actively maintained. Use tagged releases when available.

## Reporting a Vulnerability
1. Do not open a public issue for potential security problems.
2. Contact the maintainers at `security@deepfake-demo.local` with a detailed report.
3. Allow up to 5 business days for acknowledgment.
4. Provide synthetic or redacted samples only—never share real biometric data.

## Hardening Checklist
- Validate uploads (see `backend/utils/preprocess.py`).
- Keep dependencies updated (see `requirements*.txt`).
- Avoid external network calls from detectors.
- Log operational data only; never persist sensitive media.
- Run behind TLS-terminating reverse proxies in production.
- Rotate and restrict access to generated PDF reports under `logs/`.

## Dependency Security
- Use `make install` to fetch pinned dependencies.
- Update dependencies regularly and rerun `make lint typecheck test` to verify stability.

## Incident Response
- Capture timestamps, request IDs (if available), and anonymized traces when investigating.
- Revoke or rotate any affected credentials (none are expected in this demo).
- Publish remediation steps in the changelog or release notes when fixed.
