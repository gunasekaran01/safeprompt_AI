"""
Profile API routes.

Exposes GET/PATCH /api/profile, both protected by get_current_user — a
user can only ever read or update their own profile, never anyone
else's.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services import profile_service

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("", response_model=ProfileResponse, summary="Get the current user's profile")
def get_my_profile(current_user: CurrentUser = Depends(get_current_user)) -> ProfileResponse:
    try:
        profile = profile_service.get_profile(current_user.id, email=current_user.email)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to load profile.") from exc

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. It should be created automatically on sign-up.",
        )
    return ProfileResponse(**profile)


@router.patch("", response_model=ProfileResponse, summary="Update the current user's profile")
def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ProfileResponse:
    try:
        updated = profile_service.update_profile(
            current_user.id,
            {"name": payload.name, "avatar_url": payload.avatar_url},
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to update profile.") from exc

    if updated is None:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return ProfileResponse(**updated)
