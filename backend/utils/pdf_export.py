"""PDF report generation utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .logger import get_logger

logger = get_logger(__name__)


def export_report(output_path: Path, summary: dict[str, str], anomalies: list[str]) -> Path:
    """Generate a PDF report with summary and anomalies."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Generating PDF report at %s", output_path)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = [Paragraph("Deepfake Detection Report", styles["Title"]), Spacer(1, 12)]
    generated_ts = datetime.now(tz=timezone.utc).isoformat()
    story.append(Paragraph(f"Generated: {generated_ts}", styles["Normal"]))
    story.append(Spacer(1, 12))
    for key, value in summary.items():
        story.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
        story.append(Spacer(1, 6))
    if anomalies:
        story.append(Paragraph("Anomalies Detected:", styles["Heading2"]))
        for anomaly in anomalies:
            story.append(Paragraph(f"- {anomaly}", styles["Normal"]))
            story.append(Spacer(1, 4))
    doc.build(story)
    logger.info("Report created")
    return output_path
