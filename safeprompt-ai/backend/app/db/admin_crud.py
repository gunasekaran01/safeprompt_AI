"""
CRUD helpers for the admin dashboard (app/api/routes/admin.py).

Every function here takes an already user-scoped `Client` (see
app.api.deps.get_current_user_client) carrying the requesting admin's own
JWT — exactly the same pattern as app/db/profile_crud.py, and
deliberately *not* the shared/service-role client app/db/crud.py uses for
the analyses/reports tables.

This works because backend/supabase/schema.sql grants three additional
"select everything" RLS policies (`profiles_select_admin`,
`analyses_select_admin`, `reports_select_admin`) that check
`profiles.is_admin = true` for `auth.uid()`. So when an admin's own
client queries these tables with no `user_id` filter, Postgres itself
returns every row — no service-role key is needed for admin visibility,
keeping the app-wide "anon key only" design intact.
"""

from typing import Any, Dict, List

from supabase import Client

PROFILES_TABLE = "profiles"
ANALYSES_TABLE = "analyses"
REPORTS_TABLE = "reports"

# Same bound as app/services/stats_service.py, for the same reason: keep
# this fast and bounded without needing a Postgres RPC function.
MAX_RECORDS_FOR_ADMIN_STATS = 5000


def list_all_profiles(client: Client) -> List[Dict[str, Any]]:
    """
    Returns every user's profile row, newest-first. Only returns more
    than the caller's own row if they're an admin (profiles_select_admin
    RLS policy) — otherwise Postgres silently limits this to one row,
    matching profiles_select_own.
    """
    response = (
        client.table(PROFILES_TABLE).select("*").order("created_at", desc=True).execute()
    )
    return response.data or []


def list_all_analyses_raw(client: Client, limit: int = MAX_RECORDS_FOR_ADMIN_STATS) -> List[Dict[str, Any]]:
    """
    Returns up to `limit` analyses across *every* user (raw dicts, since
    we need the `user_id` column for grouping — unlike
    app/db/crud.py, which strips it before building an AnalyzeResponse).
    Requires the analyses_select_admin RLS policy to return anything
    beyond the caller's own rows.
    """
    response = (
        client.table(ANALYSES_TABLE)
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


def count_all_reports(client: Client) -> int:
    """Returns the total number of generated reports across every user."""
    response = client.table(REPORTS_TABLE).select("id", count="exact").execute()
    return response.count or 0
