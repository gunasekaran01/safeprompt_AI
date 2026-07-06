"""
Profile service.

Reads and updates a user's row in the `profiles` table. Every call is
explicitly scoped to a given user_id (the authenticated caller's id,
resolved from their validated JWT — see core/security.py), so a user can
only ever see or modify their own profile. This is enforced twice: here,
via the `.eq("id", user_id)` filter, and defense-in-depth by the RLS
policies in supabase/schema.sql (relevant if this table is ever queried
with a client using the anon key instead of the backend's service role
key).
"""

from typing import Optional

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client

TABLE_NAME = "profiles"


def get_profile(user_id: str, email: Optional[str] = None) -> Optional[dict]:
    """
    Returns the profile row for user_id, or None if it doesn't exist.

    In local-data-store mode (see core/config.py), there's no Postgres
    trigger to auto-create a profile on signup the way
    supabase/schema.sql's handle_new_user() does against a real Supabase
    project, so a missing profile is seeded here on first access instead
    (same effect, just triggered from the read path rather than signup).
    """
    client = get_supabase_client()
    response = client.table(TABLE_NAME).select("*").eq("id", user_id).limit(1).execute()
    if response.data:
        return response.data[0]

    if get_settings().USE_LOCAL_DATA_STORE:
        seeded = client.table(TABLE_NAME).insert(
            {"id": user_id, "name": None, "email": email or "", "avatar_url": None}
        ).execute()
        return seeded.data[0] if seeded.data else None

    return None


def update_profile(user_id: str, updates: dict) -> Optional[dict]:
    """
    Applies a partial update (only keys with non-None values) to the
    user's profile and returns the updated row, or None if no profile
    exists for user_id.
    """
    payload = {key: value for key, value in updates.items() if value is not None}
    if not payload:
        return get_profile(user_id)

    client = get_supabase_client()
    response = client.table(TABLE_NAME).update(payload).eq("id", user_id).execute()
    return response.data[0] if response.data else None
