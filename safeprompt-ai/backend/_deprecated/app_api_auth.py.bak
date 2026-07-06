"""
Auth API routes.

Exposes GET /api/auth/me, a protected endpoint that returns the identity
of the currently authenticated user. The frontend can call this to
confirm a stored session is still valid server-side (not just present in
the browser), and it doubles as a reference implementation for how every
other protected endpoint should use `get_current_user`.
"""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/me", response_model=CurrentUser, summary="Get the current authenticated user")
def get_me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Returns the identity resolved from the caller's Supabase JWT."""
    return current_user
