"""
Profile routes — SaaS Phase 2 (read/edit) and Phase 7 (delete).

GET /api/profiles/me returns (lazily creating on first call) the
authenticated user's profile. PATCH /api/profiles/me lets them edit it.
Both use app.api.deps.get_current_user_client, so every query here runs
against a Supabase client scoped to that user's own JWT — see
app/db/profile_crud.py's docstring for why that matters (RLS via
auth.uid(), not application-level filtering, is what actually prevents
cross-user access).

DELETE /api/profiles/me permanently deletes the account. Unlike the two
routes above, this doesn't go through profile_crud/the user-scoped
client at all — deleting an auth.users row is an admin (service-role)
operation, not a `profiles` table query, so it's delegated to
app/services/account_service.py instead. See that module's docstring
for why it needs the service-role key specifically.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import CurrentUser, get_current_user, get_current_user_client
from app.db import profile_crud
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services import account_service

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileResponse)
async def read_my_profile(
    current_user: CurrentUser = Depends(get_current_user),
    client: Client = Depends(get_current_user_client),
) -> ProfileResponse:
    """Returns the authenticated user's profile, creating it on first access."""
    profile = profile_crud.get_or_create_profile(
        client,
        user_id=current_user.id,
        email=current_user.email or "",
        name=None,
    )
    return ProfileResponse(**profile)


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    updates: ProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    client: Client = Depends(get_current_user_client),
) -> ProfileResponse:
    """
    Updates the authenticated user's name and/or avatar_url. Ensures the
    profile row exists first (get_or_create_profile) so a user editing
    their profile before it's ever been fetched still works.
    """
    profile_crud.get_or_create_profile(
        client, user_id=current_user.id, email=current_user.email or ""
    )

    fields_to_update = updates.model_dump(exclude_unset=True)
    if not fields_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update (name, avatar_url).",
        )

    updated = profile_crud.update_profile(client, current_user.id, fields_to_update)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return ProfileResponse(**updated)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(current_user: CurrentUser = Depends(get_current_user)) -> None:
    """
    Permanently deletes the authenticated user's account and everything
    they own — profile, analyses, reports, settings — via cascading
    foreign keys (see backend/supabase/schema.sql). This cannot be
    undone: there's no confirmation step at this layer, so the frontend
    (frontend/src/components/Settings/DeleteAccountSection.jsx) is
    responsible for making sure the user really means it before calling
    this.
    """
    account_service.delete_account(current_user.id)
