"""
PDF safety report generation.

New module (Milestone 13, wired for real this time) that renders a
single analysis record — the same dict shape returned by
app/services/history_service.py's get_analysis_record(), which is the
shape actually persisted by the currently-active analyze flow
(app/api/analysis.py) — into a one-page PDF using reportlab.

This intentionally does NOT reuse app/db/crud.py or the
app.schemas.analysis.AnalyzeResponse model: that whole subtree imports a
schema class that no longer exists in this codebase and cannot run. This
module instead builds directly off the dict fields history_service
already produces (safety_score, injection_detected, toxicity_detected,
etc.), so it works with the data that is actually being written today.

PDFs are written to <project_root>/reports/, matching the top-level
`reports/` folder described in README.md's project structure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import get_settings

# app/services/report_pdf_service.py -> services -> app -> backend -> safeprompt-ai (project root)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

RISK_LEVEL_COLORS = {
    "safe": colors.HexColor("#16a34a"),
    "low": colors.HexColor("#65a30d"),
    "medium": colors.HexColor("#d97706"),
    "high": colors.HexColor("#ea580c"),
    "critical": colors.HexColor("#dc2626"),
}


def _reports_dir() -> Path:
    """
    Resolves Settings.REPORTS_DIR (default "reports") to an absolute path,
    relative to the project root when given as a relative path -- e.g.
    the default "reports" resolves to <project_root>/reports, matching
    the top-level reports/ folder in README.md's project structure.
    Reads get_settings() on every call (rather than caching the resolved
    path at import time) specifically so tests can monkeypatch
    Settings.REPORTS_DIR to a tmp_path per-test and have it actually take
    effect -- this previously used a hardcoded module-level _REPORTS_DIR
    that ignored the setting entirely, so every test run was silently
    writing PDFs into the real project reports/ folder regardless of
    what tests monkeypatched.
    """
    configured = Path(get_settings().REPORTS_DIR)
    directory = configured if configured.is_absolute() else _PROJECT_ROOT / configured
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _report_filename(analysis_id: str) -> str:
    return f"safeprompt-report-{analysis_id}.pdf"


def _escape(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_pdf(record: Dict[str, Any], destination: Path) -> None:
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=20,
        textColor=colors.HexColor("#1e293b"), spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=10,
        textColor=colors.HexColor("#64748b"), spaceAfter=18,
    )
    heading_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#1e293b"), spaceBefore=16, spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10.5, leading=15,
        textColor=colors.HexColor("#334155"),
    )
    prompt_style = ParagraphStyle(
        "PromptBlock", parent=body_style,
        backColor=colors.HexColor("#f1f5f9"), borderPadding=8,
    )

    risk_level = record.get("risk_level", "medium")
    risk_color = RISK_LEVEL_COLORS.get(risk_level, colors.grey)

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=LETTER,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title=f"SafePrompt AI Safety Report — {record.get('id', '')}",
    )

    story = []
    story.append(Paragraph("SafePrompt AI — Safety Report", title_style))

    created_at = record.get("created_at", "")
    story.append(
        Paragraph(
            f"Analysis ID: {_escape(str(record.get('id', '')))} "
            f"&nbsp;&nbsp;|&nbsp;&nbsp; Generated: {_escape(str(created_at))}",
            subtitle_style,
        )
    )

    summary_data = [
        ["Safety Score", f"{record.get('safety_score', 0):.1f} / 100"],
        ["Risk Level", str(risk_level).upper()],
        ["Prompt Injection Detected", "Yes" if record.get("injection_detected") else "No"],
        ["Toxicity Detected", "Yes" if record.get("toxicity_detected") else "No"],
        ["Injection Confidence", f"{record.get('injection_confidence', 0) * 100:.0f}%"],
        ["Toxicity Confidence", f"{record.get('toxicity_confidence', 0) * 100:.0f}%"],
    ]
    summary_table = Table(summary_data, colWidths=[2.4 * inch, 3.6 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10.5),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
                ("BACKGROUND", (1, 1), (1, 1), risk_color),
                ("TEXTCOLOR", (1, 1), (1, 1), colors.white),
                ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(summary_table)

    story.append(Paragraph("Submitted Prompt", heading_style))
    story.append(Paragraph(_escape(record.get("prompt", "")), prompt_style))

    story.append(Paragraph("Recommendation", heading_style))
    story.append(Paragraph(_escape(record.get("recommendation", "")) or "No recommendation provided.", body_style))

    story.append(Paragraph("Reasoning", heading_style))
    story.append(Paragraph(_escape(record.get("reasoning", "")) or "No additional reasoning was recorded.", body_style))

    if record.get("injection_detected"):
        story.append(Paragraph("Injection Detail", heading_style))
        story.append(Paragraph(_escape(record.get("injection_reason", "")), body_style))

    if record.get("toxicity_detected"):
        story.append(Paragraph("Toxicity Detail", heading_style))
        category = record.get("toxicity_category", "none")
        story.append(Paragraph(f"Category: {_escape(str(category))}", body_style))
        story.append(Paragraph(_escape(record.get("toxicity_explanation", "")), body_style))

    story.append(Spacer(1, 24))
    story.append(
        Paragraph(
            "Generated by SafePrompt AI — Prompt Injection and Toxicity Detection Platform.",
            subtitle_style,
        )
    )

    doc.build(story)


def generate_report_pdf(record: Dict[str, Any]) -> Path:
    """
    Renders `record` (a history_service analysis dict) to a PDF file
    under <project_root>/reports/ and returns the absolute path.
    Regenerating for the same analysis id overwrites the previous file.
    """
    destination = _reports_dir() / _report_filename(record["id"])
    _build_pdf(record, destination)
    return destination
