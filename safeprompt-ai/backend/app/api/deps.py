"""
Authentication dependencies for protected FastAPI routes.

SaaS Phase 1: validates the Supabase-issued JWT the frontend sends in the
Authorization header (see frontend/src/services/apiClient.js) by asking
Supabase's own Auth server to verify it (GoTrue's GET /auth/v1/user),
rather than verifying the JWT signature locally. That means this backend
never needs the project's JWT secret — consistent with its anon-key-only
design (see app/db/supabase_client.py) — at the cost of one extra HTTP
round-trip per authenticated request, which is an acceptable trade for a
project this size.

Only GET /api/auth/me (app/api/routes/auth.py) uses this today. Phase 4
of the SaaS migration will add this same dependency to the
analyses/history/stats/reports routes so every query can be scoped to
`current_user.id`, once those tables have a user_id column (Phase 3).
"""

from fastapi import Depends, Header, HTTPException, status
from supabase import Client

from app.core.config import get_settings
from app.db.supabase_client import get_supabase_client, get_user_scoped_client


class CurrentUser:
    """Minimal authenticated-user info extracted from a validated Supabase JWT."""

    def __init__(self, id: str, email: str | None, access_token: str) -> None:
        self.id = id
        self.email = email
        # Kept so callers that need per-user RLS (e.g. app/db/profile_crud.py,
        # via get_current_user_client below) can build a client scoped to
        # this exact user, rather than the shared anon/service-role client.
        self.access_token = access_token


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


# Delegate authentication to the shared, tested implementation in app.core.security
# so test patches against app.core.security.get_supabase_client or that module
# take effect for both modules.
from app.core.security import get_current_user as _core_get_current_user

# Keep the same exported name so routes can depend on it as before.
get_current_user = _core_get_current_user


async def get_current_user_client(current_user: CurrentUser = Depends(get_current_user)) -> Client:
    """
    Convenience dependency for routes that need both the authenticated
    user *and* a Supabase client scoped to that same user (i.e. anything
    reading/writing a table with per-user RLS, like `profiles` — see
    app/db/profile_crud.py). Reuses get_current_user so the JWT is only
    validated once per request.
    """
    return get_user_scoped_client(current_user.access_token)


def is_admin_email(email: str | None) -> bool:
    """
    Checks `email` against Settings.ADMIN_EMAILS (case-insensitive).
    Shared by `require_admin` below and GET /api/auth/me (which surfaces
    `is_admin` to the frontend so it knows whether to show the Admin nav
    link/route at all).
    """
    if not email:
        return False
    return email.strip().lower() in get_settings().admin_emails_list


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user),
    client: Client = Depends(get_current_user_client),
) -> CurrentUser:
    """
    FastAPI dependency for admin-only routes (app/api/routes/admin.py).
    Requires a valid session (via get_current_user) *and* that the user's
    email is in Settings.ADMIN_EMAILS, raising 403 otherwise.

    This is the app-layer gate; it exists so an admin-only endpoint
    returns a clean 403 instead of an empty/partial result if it were
    left to RLS alone. The actual data-access boundary is still RLS (the
    `is_admin` column and admin SELECT policies in
    backend/supabase/schema.sql) — this dependency also returns a
    user-scoped `Client` on `current_user`-adjacent routes via the same
    `get_current_user_client` dependency, so admin routes query through
    that client and only see everything because Postgres, not this
    check, grants it.
    """
    if not is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin access.",
        )
    return current_user
