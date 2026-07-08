"""
History & dashboard-stats service.

Every function here is explicitly scoped to a given user_id, resolved
from the caller's validated JWT (see core/security.py). This is the
actual enforcement layer for per-user data isolation through our API —
recall that the backend connects with the Supabase SERVICE ROLE key,
which bypasses RLS entirely, so RLS alone would NOT protect this data if
these functions ever forgot to filter by user_id. Every query below
explicitly does.
"""

import logging
from typing import Optional

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client
from app.schemas.analysis import PromptAnalysisResponse

logger = logging.getLogger(__name__)

ANALYSES_TABLE = "analyses"
REPORTS_TABLE = "reports"
STATS_VIEW = "analyses_stats"


def create_analysis_record(user_id: str, analysis: PromptAnalysisResponse) -> Optional[dict]:
    """
    Persists a completed analysis for user_id. Failures are logged but
    not raised, so a database outage never breaks the core /api/analyze
    response the user is waiting on.
    """
    payload = {
        "user_id": user_id,
        "prompt": analysis.prompt,
        "injection_detected": analysis.injection.detected,
        "injection_confidence": analysis.injection.confidence,
        "injection_reason": analysis.injection.reason,
        "toxicity_detected": analysis.toxicity.detected,
        "toxicity_category": analysis.toxicity.category,
        "toxicity_confidence": analysis.toxicity.confidence,
        "toxicity_explanation": analysis.toxicity.explanation,
        "safety_score": analysis.safety_score,
        "risk_level": analysis.risk_level,
        "recommendation": analysis.recommendation,
        "reasoning": analysis.reasoning,
    }
    try:
        client = get_supabase_client()
        response = client.table(ANALYSES_TABLE).insert(payload).execute()
        return response.data[0] if response.data else None
    except Exception:  # noqa: BLE001
        logger.exception("Failed to persist analysis record for user %s.", user_id)
        return None


def list_analysis_records(
    user_id: str,
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    injection_only: bool = False,
    toxicity_only: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """
    Returns (records, total_count) for user_id's history, most recent
    first, with optional case-insensitive prompt search, risk-level
    filter, and injection/toxicity-only filters. ALWAYS filtered by
    user_id — never returns another user's rows.
    """
    client = get_supabase_client()
    query = client.table(ANALYSES_TABLE).select("*", count="exact").eq("user_id", user_id)

    if search:
        query = query.ilike("prompt", f"%{search}%")
    if risk_level:
        query = query.eq("risk_level", risk_level)
    if injection_only:
        query = query.eq("injection_detected", True)
    if toxicity_only:
        query = query.eq("toxicity_detected", True)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    response = query.execute()
    return response.data or [], response.count or 0


def get_analysis_record(user_id: str, record_id: str) -> Optional[dict]:
    """Returns a single record only if it belongs to user_id."""
    client = get_supabase_client()
    response = (
        client.table(ANALYSES_TABLE)
        .select("*")
        .eq("id", record_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_analysis_record(user_id: str, record_id: str) -> bool:
    """Deletes a record only if it belongs to user_id."""
    client = get_supabase_client()
    response = (
        client.table(ANALYSES_TABLE).delete().eq("id", record_id).eq("user_id", user_id).execute()
    )
    return bool(response.data)


def _empty_dashboard_stats(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "total_analyses": 0,
        "safe_prompts": 0,
        "unsafe_prompts": 0,
        "injection_attempts": 0,
        "toxic_prompts": 0,
        "average_safety_score": 0,
        "safe_count": 0,
        "low_count": 0,
        "medium_count": 0,
        "high_count": 0,
        "critical_count": 0,
    }


def get_dashboard_stats(user_id: str) -> dict:
    """
    Returns aggregate stats for user_id.

    Against a real Supabase project this reads the pre-aggregated
    `analyses_stats` Postgres view. The local in-memory data store (see
    core/config.py's USE_LOCAL_DATA_STORE) has no such view, so in that
    mode the same aggregation is computed here in Python over the
    user's own `analyses` rows instead.
    """
    client = get_supabase_client()

    if get_settings().USE_LOCAL_DATA_STORE:
        rows = client.table(ANALYSES_TABLE).select("*").eq("user_id", user_id).execute().data or []
        if not rows:
            return _empty_dashboard_stats(user_id)
        scores = [row.get("safety_score", 0) for row in rows]
        return {
            "user_id": user_id,
            "total_analyses": len(rows),
            "safe_prompts": sum(1 for r in rows if r.get("risk_level") in ("safe", "low")),
            "unsafe_prompts": sum(1 for r in rows if r.get("risk_level") in ("medium", "high", "critical")),
            "injection_attempts": sum(1 for r in rows if r.get("injection_detected")),
            "toxic_prompts": sum(1 for r in rows if r.get("toxicity_detected")),
            "average_safety_score": sum(scores) / len(scores) if scores else 0,
            "safe_count": sum(1 for r in rows if r.get("risk_level") == "safe"),
            "low_count": sum(1 for r in rows if r.get("risk_level") == "low"),
            "medium_count": sum(1 for r in rows if r.get("risk_level") == "medium"),
            "high_count": sum(1 for r in rows if r.get("risk_level") == "high"),
            "critical_count": sum(1 for r in rows if r.get("risk_level") == "critical"),
        }

    response = client.table(STATS_VIEW).select("*").eq("user_id", user_id).limit(1).execute()
    if response.data:
        return response.data[0]
    return _empty_dashboard_stats(user_id)


def get_recent_activity(user_id: str, limit: int = 8) -> list[dict]:
    """Returns user_id's most recent analyses."""
    client = get_supabase_client()
    response = (
        client.table(ANALYSES_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


def create_report_record(user_id: str, analysis_id: str, file_path: str) -> Optional[dict]:
    """
    Records a generated PDF report in the `reports` table, owned by
    `user_id`. Called by app/api/reports.py right after
    report_pdf_service renders the PDF to disk, so every generation is
    auditable and shows up in admin's report count. Failures are logged
    but not raised -- a database hiccup here shouldn't prevent the user
    from downloading a PDF that already rendered successfully.

    Payload matches the `reports` table columns in
    backend/supabase/schema.sql exactly (id/generated_at are filled in
    by the column defaults there, or by LocalDataStore's equivalent
    fallback when USE_LOCAL_DATA_STORE=True) -- unlike the older,
    unwired app/db/crud.py:create_report, which also sends a `format`
    key that has no matching column and would be rejected by PostgREST.
    """
    payload = {
        "user_id": user_id,
        "analysis_id": analysis_id,
        "file_path": file_path,
    }
    try:
        client = get_supabase_client()
        response = client.table(REPORTS_TABLE).insert(payload).execute()
        return response.data[0] if response.data else None
    except Exception:  # noqa: BLE001
        logger.exception(
            "Failed to persist report record for analysis %s (user %s).", analysis_id, user_id
        )
        return None
