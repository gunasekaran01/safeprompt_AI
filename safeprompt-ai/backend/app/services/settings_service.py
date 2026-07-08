"""
Service layer for the `user_settings` table (Phase 7).

Follows the same convention as app/services/history_service.py: calls
the shared get_supabase_client() (service-role in real Supabase mode,
the in-memory LocalDataStore in local-dev mode) and explicitly filters
by user_id in application code -- see the architecture note at the top
of backend/supabase/schema.sql's Phase 3 section for why that's the
actual enforcement boundary through this API, with RLS as defense in
depth for any client that queries Supabase directly.

One row per user. GET lazily creates the row with defaults on first
access (mirrors app/db/profile_crud.py's get_or_create_profile), so a
brand-new user's first visit to Settings "just works" with no separate
provisioning step.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.db.supabase_client import get_supabase_client

TABLE_NAME = "user_settings"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "system",
    "compact_mode": False,
    "auto_analyze_on_paste": False,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_row(user_id: str) -> Optional[Dict[str, Any]]:
    client = get_supabase_client()
    result = client.table(TABLE_NAME).select("*").eq("user_id", user_id).limit(1).execute()
    rows = result.data or []
    return rows[0] if rows else None


def _create_row(user_id: str) -> Dict[str, Any]:
    client = get_supabase_client()
    payload = {"user_id": user_id, "updated_at": _now_iso(), **DEFAULT_SETTINGS}
    result = client.table(TABLE_NAME).insert(payload).execute()
    return result.data[0]


def get_or_create_settings(user_id: str) -> Dict[str, Any]:
    """Returns the user's settings row, creating it with defaults if this is their first visit."""
    existing = _get_row(user_id)
    if existing is not None:
        return existing
    return _create_row(user_id)


def update_settings(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies a partial update (only keys the caller actually sent), and
    bumps updated_at. Creates the row first if this user has never had
    one, so PATCH works even before the user has ever opened Settings.
    """
    get_or_create_settings(user_id)
    clean_updates = {key: value for key, value in updates.items() if value is not None}
    clean_updates["updated_at"] = _now_iso()

    client = get_supabase_client()
    result = (
        client.table(TABLE_NAME)
        .update(clean_updates)
        .eq("user_id", user_id)
        .execute()
    )
    rows = result.data or []
    return rows[0] if rows else get_or_create_settings(user_id)
