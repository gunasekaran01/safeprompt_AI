"""
Auth routes — SaaS Phase 1.

Sign up / login / logout / password reset are all performed client-side
by the frontend via @supabase/supabase-js talking directly to Supabase
Auth (see frontend/src/context/AuthContext.jsx) — this backend never
handles passwords or issues its own tokens.

What *does* belong here is verifying that a bearer token the frontend
sends really is a valid, current Supabase session. GET /api/auth/me is
that check: it's the building block every future protected route
(Phase 4: analyses/history/stats/reports scoped to the authenticated
user) will depend on via app.api.deps.get_current_user, and it gives the
frontend a simple way to confirm "is my session good, according to this
backend" independent of Supabase's own client-side session state.
"""

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user, is_admin_email
from app.schemas.auth import CurrentUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUserResponse)
async def read_current_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUserResponse:
    """Returns the authenticated user's id/email/admin status, or 401 if the bearer token is missing/invalid."""
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        is_admin=is_admin_email(current_user.email),
    )
