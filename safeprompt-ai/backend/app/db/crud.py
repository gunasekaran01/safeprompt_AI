"""
CRUD helpers — Supabase edition, scoped to the authenticated user.

Every function here goes through `get_supabase_client()`
(app/db/supabase_client.py), which uses the service-role key when
configured — meaning it bypasses Row Level Security entirely. That's a
deliberate choice (see that module's docstring), but it means RLS is
*not* what keeps one user's analyses/reports away from another's here:
every function below takes an explicit `user_id` and filters by it in
the query itself. The route layer (app/api/routes/analysis.py,
history.py, stats.py, reports.py) gets that id from
app.api.deps.get_current_user and must always pass it through — there
is no "unscoped" variant of any of these functions left to call by
mistake.

(Contrast this with app/db/profile_crud.py, which uses a *user-scoped*
client via app.api.deps.get_current_user_client — there, RLS is the
actual enforcement boundary, because that client carries the user's own
JWT rather than the service-role key.)

`get_supabase_client` is imported and called fresh inside each function
so tests can monkeypatch `app.db.crud.get_supabase_client` with a fake
in-memory client (see backend/tests/conftest.py / fake_supabase.py)
without needing real Supabase credentials.
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.db.supabase_client import get_supabase_client
from app.schemas.analysis import AnalyzeResponse


ANALYSES_TABLE = "analyses"
REPORTS_TABLE = "reports"


def _serialize(analysis: AnalyzeResponse, user_id: str) -> dict:
    """Converts an AnalyzeResponse into a JSON-safe dict for Supabase, owned by `user_id`."""
    return {
        "id": analysis.id,
        "user_id": user_id,
        "prompt": analysis.prompt,
        "timestamp": analysis.timestamp.isoformat(),
        "score": analysis.score,
        "risk_level": analysis.risk_level,
        "injection_detected": analysis.injection_detected,
        "toxicity_detected": analysis.toxicity_detected,
        "injection_confidence": analysis.injection_confidence,
        "toxicity_scores": analysis.toxicity_scores,
        "recommendation": analysis.recommendation,
        "reasoning": analysis.reasoning,
    }


def _apply_common_filters(
    query,
    user_id: str,
    risk_level: Optional[str],
    search: Optional[str],
    injection_only: bool,
    toxicity_only: bool,
):
    """Applies the ownership scope plus the History/Stats filter set shared by list/count queries."""
    query = query.eq("user_id", user_id)
    if risk_level:
        query = query.eq("risk_level", risk_level)
    if injection_only:
        query = query.eq("injection_detected", True)
    if toxicity_only:
        query = query.eq("toxicity_detected", True)
    if search:
        query = query.ilike("prompt", f"%{search}%")
    return query


# --- analyses --------------------------------------------------------------


def create_analysis(analysis: AnalyzeResponse, user_id: str) -> AnalyzeResponse:
    """Persists an AnalyzeResponse as a new row in the `analyses` table, owned by `user_id`."""
    client = get_supabase_client()
    payload = _serialize(analysis, user_id)
    response = client.table(ANALYSES_TABLE).insert(payload).execute()
    if not response.data:
        raise RuntimeError("Supabase insert into 'analyses' returned no data.")
    return analysis


def get_analysis(analysis_id: str, user_id: str) -> Optional[AnalyzeResponse]:
    """
    Fetches a single analysis by its id, scoped to `user_id`. Returns None
    if it doesn't exist *or* belongs to a different user — the two cases
    are indistinguishable to the caller by design, so a route can never
    leak "that record exists, it's just not yours" to an unauthorized
    caller.
    """
    client = get_supabase_client()
    response = (
        client.table(ANALYSES_TABLE)
        .select("*")
        .eq("id", analysis_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return AnalyzeResponse(**{k: v for k, v in rows[0].items() if k != "user_id"}) if rows else None


def list_analyses(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    injection_only: bool = False,
    toxicity_only: bool = False,
) -> List[AnalyzeResponse]:
    """Returns a page of `user_id`'s own analyses, newest first, with optional filtering."""
    client = get_supabase_client()
    query = client.table(ANALYSES_TABLE).select("*")
    query = _apply_common_filters(query, user_id, risk_level, search, injection_only, toxicity_only)
    query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)
    response = query.execute()
    return [AnalyzeResponse(**{k: v for k, v in row.items() if k != "user_id"}) for row in response.data or []]


def count_analyses(
    user_id: str,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    injection_only: bool = False,
    toxicity_only: bool = False,
) -> int:
    """Returns the total number of `user_id`'s own analyses matching the given filters."""
    client = get_supabase_client()
    query = client.table(ANALYSES_TABLE).select("id", count="exact")
    query = _apply_common_filters(query, user_id, risk_level, search, injection_only, toxicity_only)
    response = query.execute()
    return response.count or 0


def delete_analysis(analysis_id: str, user_id: str) -> bool:
    """
    Deletes a single analysis by id, scoped to `user_id`. Returns True if
    a row was deleted — always False if the analysis belongs to someone
    else, since the `.eq("user_id", user_id)` filter means the delete
    simply matches zero rows rather than raising.
    """
    client = get_supabase_client()
    response = (
        client.table(ANALYSES_TABLE)
        .delete()
        .eq("id", analysis_id)
        .eq("user_id", user_id)
        .execute()
    )
    return bool(response.data)


def list_all_analyses(user_id: str, limit: int = 5000) -> List[AnalyzeResponse]:
    """
    Returns up to `limit` of `user_id`'s own analyses, newest first, with
    no other filtering. Used by app/services/stats_service.py to compute
    that user's chart aggregates in Python over their own data only.
    """
    client = get_supabase_client()
    response = (
        client.table(ANALYSES_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return [AnalyzeResponse(**{k: v for k, v in row.items() if k != "user_id"}) for row in response.data or []]


# --- reports -----------------------------------------------------------


def create_report(analysis_id: str, file_path: str, user_id: str) -> dict:
    """
    Records a generated PDF report in the `reports` table, owned by
    `user_id`. Used by app/services/report_service.py right after
    rendering a PDF to disk. Returns the inserted row as a dict.
    """
    client = get_supabase_client()
    payload = {
        "analysis_id": analysis_id,
        "user_id": user_id,
        "file_path": file_path,
        "format": "pdf",
        # Set explicitly rather than relying on Postgres's column default,
        # so ordering by this field also works against the in-memory fake
        # client used in tests (tests/fake_supabase.py has no concept of
        # column defaults).
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    response = client.table(REPORTS_TABLE).insert(payload).execute()
    if not response.data:
        raise RuntimeError("Supabase insert into 'reports' returned no data.")
    return response.data[0]


def list_reports_for_analysis(analysis_id: str, user_id: str) -> List[dict]:
    """Returns all of `user_id`'s own report records for a given analysis, newest first."""
    client = get_supabase_client()
    response = (
        client.table(REPORTS_TABLE)
        .select("*")
        .eq("analysis_id", analysis_id)
        .eq("user_id", user_id)
        .order("generated_at", desc=True)
        .execute()
    )
    return response.data or []
