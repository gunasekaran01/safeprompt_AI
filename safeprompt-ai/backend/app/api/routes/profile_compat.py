from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user, CurrentUser
from app.services import profile_service
from app.db import profile_crud
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def read_profile(current_user: CurrentUser = Depends(get_current_user)) -> ProfileResponse:
    client = profile_service.get_supabase_client()
    profile = profile_crud.get_profile(client, current_user.id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return ProfileResponse(**profile)


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(updates: ProfileUpdateRequest, current_user: CurrentUser = Depends(get_current_user)) -> ProfileResponse:
    client = profile_service.get_supabase_client()
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
