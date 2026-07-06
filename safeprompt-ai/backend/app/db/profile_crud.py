"""
CRUD helpers for the `profiles` table (SaaS Phase 2).

Unlike app/db/crud.py — where every function calls the shared
get_supabase_client() (anon key, or service_role if configured) — every
function here takes an already user-scoped `Client` as its first
argument (see app.db.supabase_client.get_user_scoped_client, obtained via
app.api.deps.get_current_user_client). That client carries the
requesting user's own JWT, so the `profiles_owner_only` RLS policy in
supabase/schema.sql (auth.uid() = id) restricts every query here to that
user's own row — there is no way, under RLS, for this code to
accidentally read or write another user's profile, regardless of what id
it's given.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from supabase import Client

TABLE_NAME = "profiles"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_profile(client: Client, user_id: str) -> Optional[Dict[str, Any]]:
    """Returns the profile row for `user_id`, or None if it doesn't exist yet."""
    result = client.table(TABLE_NAME).select("*").eq("id", user_id).limit(1).execute()
    rows = result.data or []
    return rows[0] if rows else None


def create_profile(
    client: Client, *, user_id: str, email: str, name: Optional[str] = None
) -> Dict[str, Any]:
    """Inserts a new profile row for `user_id`."""
    now = _now_iso()
    payload = {
        "id": user_id,
        "email": email,
        "name": name,
        "avatar_url": None,
        "created_at": now,
        "updated_at": now,
    }
    result = client.table(TABLE_NAME).insert(payload).execute()
    return result.data[0]


def update_profile(
    client: Client, user_id: str, updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Applies a partial update to `user_id`'s profile (e.g. name/avatar_url)
    and bumps `updated_at`. Returns the updated row, or None if no row
    with that id exists (RLS also means this can never touch a row
    belonging to a different user, even if a bug ever passed one in).
    """
    payload = {**updates, "updated_at": _now_iso()}
    result = client.table(TABLE_NAME).update(payload).eq("id", user_id).execute()
    rows = result.data or []
    return rows[0] if rows else None


def get_or_create_profile(
    client: Client, *, user_id: str, email: str, name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns the user's profile, lazily creating it on first access.

    The `profiles` table has no DB trigger populating a row on signup
    (see supabase/schema.sql) — keeping profile creation here, in
    application code, means it stays visible and testable rather than
    hidden in a Postgres trigger. GET /api/profiles/me calls this so a
    user's very first request after verifying their email "just works"
    without a separate provisioning step.
    """
    existing = get_profile(client, user_id)
    if existing is not None:
        return existing
    return create_profile(client, user_id=user_id, email=email, name=name)
