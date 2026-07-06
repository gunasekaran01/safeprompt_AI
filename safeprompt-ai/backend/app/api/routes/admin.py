"""
Admin routes.

Platform-wide visibility for the SafePrompt AI admin account (see
Settings.ADMIN_EMAILS, backend/.env.example) — total users, total
analyses/reports across everyone, and a per-user breakdown, plus the
ability to delete a user's account.

Every route requires app.api.deps.require_admin (checks the caller's
email against Settings.ADMIN_EMAILS) *and* runs its Supabase queries
through the caller's own JWT-scoped client
(app.api.deps.get_current_user_client) rather than a shared/service-role
client. Visibility across users is granted by Postgres itself, via the
`profiles_select_admin` / `analyses_select_admin` / `reports_select_admin`
RLS policies in backend/supabase/schema.sql (which check
`profiles.is_admin = true` for the caller) — so this works with only
SUPABASE_ANON_KEY configured, no service-role key required.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import CurrentUser, get_current_user_client, require_admin
from app.schemas.admin import AdminOverviewResponse, AdminUsersResponse
from app.services import admin_service
from app.services.account_service import delete_account

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/overview", response_model=AdminOverviewResponse, summary="Platform-wide stats")
def get_admin_overview(
    _admin: CurrentUser = Depends(require_admin),
    client: Client = Depends(get_current_user_client),
) -> AdminOverviewResponse:
    """Returns total users/analyses/reports and a risk-level breakdown across every user."""
    return admin_service.compute_admin_overview(client)


@router.get("/users", response_model=AdminUsersResponse, summary="List every user")
def get_admin_users(
    _admin: CurrentUser = Depends(require_admin),
    client: Client = Depends(get_current_user_client),
) -> AdminUsersResponse:
    """Returns every user's profile plus their analysis count, newest signups first."""
    return admin_service.list_users_with_counts(client)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete a user's account",
)
def delete_admin_user(
    user_id: str,
    admin: CurrentUser = Depends(require_admin),
) -> None:
    """
    Permanently deletes any user's account (and everything they own, via
    cascading foreign keys — see app/services/account_service.py). An
    admin cannot delete their own account through this endpoint — use
    DELETE /api/profiles/me for that instead — so this stays purely a
    "manage other users" action and never causes an admin to
    accidentally lock themselves out mid-session.
    """
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use DELETE /api/profiles/me to delete your own account.",
        )
    delete_account(user_id)
