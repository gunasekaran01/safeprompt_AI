"""
PDF safety report generation — Milestone 13.

Renders a single `analyses` row (app/schemas/analysis.py:AnalyzeResponse)
into a one-page PDF safety report using reportlab, saves it to disk under
Settings.REPORTS_DIR (backend/reports/ by default), and records the
report's metadata in the Supabase `reports` table
(app/db/crud.py:create_report) so every generation is auditable.

Only reportlab is used here — no external service, no headless-browser
HTML-to-PDF conversion — matching the `reportlab` dependency already
pinned in backend/requirements.txt.
"""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import get_settings
from app.db import crud
from app.schemas.analysis import AnalyzeResponse

# app/services/report_service.py -> app/services -> app -> backend/
_BACKEND_DIR = Path(__file__).resolve().parents[2]

RISK_LEVEL_COLORS = {
    "safe": colors.HexColor("#16a34a"),
    "low": colors.HexColor("#65a30d"),
    "medium": colors.HexColor("#d97706"),
    "high": colors.HexColor("#ea580c"),
    "critical": colors.HexColor("#dc2626"),
}


def _reports_dir() -> Path:
    settings = get_settings()
    path = _BACKEND_DIR / settings.REPORTS_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _report_filename(analysis_id: str) -> str:
    return f"safeprompt-report-{analysis_id}.pdf"


def _build_pdf(analysis: AnalyzeResponse, destination: Path) -> None:
    """Renders `analysis` into a one-page PDF at `destination`."""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=18,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=16,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#334155"),
    )
    prompt_style = ParagraphStyle(
        "PromptBlock",
        parent=body_style,
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=8,
    )

    risk_color = RISK_LEVEL_COLORS.get(analysis.risk_level, colors.grey)

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=LETTER,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title=f"SafePrompt AI Safety Report — {analysis.id}",
    )

    story = []

    story.append(Paragraph("SafePrompt AI — Safety Report", title_style))
    story.append(
        Paragraph(
            f"Analysis ID: {analysis.id} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Generated: {analysis.timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
            subtitle_style,
        )
    )

    # --- summary table -----------------------------------------------
    summary_data = [
        ["Safety Score", f"{analysis.score:.1f} / 100"],
        ["Risk Level", analysis.risk_level.upper()],
        ["Prompt Injection Detected", "Yes" if analysis.injection_detected else "No"],
        ["Toxicity Detected", "Yes" if analysis.toxicity_detected else "No"],
        ["Injection Confidence", f"{analysis.injection_confidence * 100:.0f}%"],
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

    # --- prompt --------------------------------------------------------
    story.append(Paragraph("Submitted Prompt", heading_style))
    escaped_prompt = (
        analysis.prompt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    story.append(Paragraph(escaped_prompt, prompt_style))

    # --- recommendation --------------------------------------------------
    story.append(Paragraph("Recommendation", heading_style))
    story.append(Paragraph(analysis.recommendation or "No recommendation provided.", body_style))

    # --- reasoning -------------------------------------------------------
    story.append(Paragraph("Reasoning", heading_style))
    if analysis.reasoning:
        items = [
            ListItem(Paragraph(reason, body_style), bulletColor=colors.HexColor("#64748b"))
            for reason in analysis.reasoning
        ]
        story.append(ListFlowable(items, bulletType="bullet", leftIndent=14))
    else:
        story.append(Paragraph("No additional reasoning was recorded.", body_style))

    # --- toxicity breakdown (only when the ML model produced scores) -----
    if analysis.toxicity_scores:
        story.append(Paragraph("Toxicity Category Scores", heading_style))
        rows = [["Category", "Score"]] + [
            [category.replace("_", " ").title(), f"{score * 100:.0f}%"]
            for category, score in sorted(
                analysis.toxicity_scores.items(), key=lambda item: item[1], reverse=True
            )
        ]
        breakdown_table = Table(rows, colWidths=[3 * inch, 3 * inch])
        breakdown_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ]
            )
        )
        story.append(breakdown_table)

    story.append(Spacer(1, 24))
    story.append(
        Paragraph(
            "Generated by SafePrompt AI — Prompt Injection and Toxicity Detection Platform.",
            subtitle_style,
        )
    )

    doc.build(story)


def generate_report_pdf(analysis: AnalyzeResponse) -> Path:
    """
    Renders `analysis` to a PDF file under Settings.REPORTS_DIR and
    returns the absolute path. Re-generating for the same analysis
    overwrites the previous file at the same deterministic path, but a
    fresh `reports` row is still recorded on every call (see
    `record_report`) so the generation history is preserved.
    """
    destination = _reports_dir() / _report_filename(analysis.id)
    _build_pdf(analysis, destination)
    return destination


def record_report(analysis_id: str, file_path: Path, user_id: str) -> None:
    """
    Records a generated report in the Supabase `reports` table, owned by
    `user_id`. Best effort: a Supabase hiccup here shouldn't prevent the
    user from downloading a PDF that was already successfully rendered
    to disk, so failures are swallowed after being surfaced via a
    raised-then-caught exception path at the call site (see
    app/api/routes/reports.py).
    """
    relative_path = os.path.relpath(file_path, _BACKEND_DIR)
    crud.create_report(analysis_id=analysis_id, file_path=relative_path, user_id=user_id)
