"""
PDF report routes — Milestone 13.

A single endpoint renders a fresh PDF safety report for a given analysis
(via app/services/report_service.py, reportlab) and streams it back as a
file download. Every successful generation is also logged to the
Supabase `reports` table for an audit trail — see
backend/supabase/schema.sql's `reports` table.

Recording the report is best-effort: if Supabase is briefly unreachable,
the user still gets their PDF (already rendered to disk) rather than a
500, since the file is the thing they actually asked for.

SaaS Phase 4: requires authentication, and can only generate a report
for an analysis owned by the requesting user — crud.get_analysis already
scopes the lookup to `user_id`, so an analysis belonging to someone else
looks identical to a nonexistent one (404).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.api.deps import CurrentUser, get_current_user
from app.db import crud
from app.services import report_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/{analysis_id}",
    summary="Generate and download a PDF safety report for an analysis",
    response_class=FileResponse,
)
def get_report(
    analysis_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> FileResponse:
    analysis = crud.get_analysis(analysis_id, user_id=current_user.id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found."
        )

    file_path = report_service.generate_report_pdf(analysis)

    try:
        report_service.record_report(analysis_id, file_path, user_id=current_user.id)
    except Exception:  # noqa: BLE001 - logging + continuing is intentional here
        logger.exception("Failed to record report metadata for analysis %s", analysis_id)

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
    )
