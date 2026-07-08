"""
PDF report routes.

New route module wired against the currently-active data path
(app/services/history_service.py), not the broken app/api/routes/reports.py
(which depends on a schema class, AnalyzeResponse, that no longer exists
in this codebase). Mounted directly in main.py alongside the other
app/api/*.py routers.

GET /api/reports/{analysis_id} looks up the analysis (scoped to the
authenticated user — a record that exists but belongs to someone else is
indistinguishable from one that doesn't exist, same convention as
history.py), renders a fresh PDF via report_pdf_service, and streams it
back as a file download.

Every generation is also recorded in the `reports` Supabase table via
app.services.history_service.create_report_record -- not
app.db.crud.create_report, an older helper that sends a `format` key
the real `reports` table schema (backend/supabase/schema.sql) has no
column for, and that a real PostgREST/Supabase insert would reject.
Against the local in-memory dev store (app/db/local_store.py, which
doesn't validate columns) that extra key was silently accepted, so this
never surfaced as a request failure locally -- it just meant every
report "successfully" recorded a shape that would break the moment this
ran against a real Supabase project.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.services import history_service, report_pdf_service

# No "/api" prefix here -- see app/api/analysis.py's comment: main.py's
# api_router mount already adds "/api", so keeping it here doubled the
# path to /api/api/reports/{analysis_id}.
router = APIRouter(prefix="", tags=["Reports"])


@router.get(
    "/reports/{analysis_id}",
    summary="Generate and download a PDF safety report for an analysis",
    response_class=FileResponse,
)
def get_report(
    analysis_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> FileResponse:
    try:
        record = history_service.get_analysis_record(current_user.id, analysis_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to load this analysis.") from exc

    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    file_path = report_pdf_service.generate_report_pdf(record)

    try:
        history_service.create_report_record(current_user.id, analysis_id, str(file_path))
    except Exception:  # noqa: BLE001
        # Metadata bookkeeping failing shouldn't block the user from
        # getting their PDF -- the file was already generated above.
        pass

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
    )
