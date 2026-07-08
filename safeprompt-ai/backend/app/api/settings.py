"""
GET/PATCH /api/settings (Phase 7).

Server-synced counterpart to the theme/compact-mode/auto-analyze
preferences the frontend previously only kept in localStorage. Mounted
into api_router (see app/api/router.py), same auth pattern as
app/api/analysis.py, history.py, and reports.py.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest
from app.services import settings_service

router = APIRouter(prefix="", tags=["Settings"])


@router.get("/settings", response_model=SettingsResponse, summary="Get the current user's settings")
def get_settings(current_user: CurrentUser = Depends(get_current_user)) -> SettingsResponse:
    try:
        row = settings_service.get_or_create_settings(current_user.id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to load settings.") from exc
    return SettingsResponse(**row)


@router.patch("/settings", response_model=SettingsResponse, summary="Update the current user's settings")
def update_settings(
    payload: SettingsUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> SettingsResponse:
    updates = payload.model_dump(exclude_unset=True)
    try:
        row = settings_service.update_settings(current_user.id, updates)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to update settings.") from exc
    return SettingsResponse(**row)
