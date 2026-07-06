"""
History & dashboard API routes.

Every route requires authentication and passes current_user.id into the
history_service functions, which explicitly filter every query by that
user_id. No route here can return another user's data.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.history import AnalysisListResponse, AnalysisRecord, DashboardStatsResponse
from app.services import history_service

# No "/api" prefix here -- see app/api/analysis.py's comment: main.py's
# api_router mount already adds "/api", so keeping it here doubled every
# path to /api/api/history, /api/api/dashboard/stats, etc.
router = APIRouter(prefix="", tags=["History"])

VALID_RISK_LEVELS = {"safe", "low", "medium", "high", "critical"}


@router.get("/history", response_model=AnalysisListResponse, summary="List the current user's analysis history")
def get_history(
    search: Optional[str] = Query(default=None, max_length=500),
    risk_level: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalysisListResponse:
    if risk_level is not None and risk_level not in VALID_RISK_LEVELS:
        raise HTTPException(
            status_code=422,
            detail=f"risk_level must be one of {sorted(VALID_RISK_LEVELS)}",
        )

    try:
        records, total = history_service.list_analysis_records(
            user_id=current_user.id,
            search=search,
            risk_level=risk_level,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Failed to load history. Ensure SUPABASE_URL/SUPABASE_KEY are configured.",
        ) from exc

    return AnalysisListResponse(
        items=[AnalysisRecord(**record) for record in records],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/history/{record_id}", response_model=AnalysisRecord, summary="Get a single analysis")
def get_history_item(
    record_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalysisRecord:
    try:
        record = history_service.get_analysis_record(current_user.id, record_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to load this analysis.") from exc

    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return AnalysisRecord(**record)


@router.delete("/history/{record_id}", status_code=204, summary="Delete a single analysis")
def delete_history_item(
    record_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    try:
        deleted = history_service.delete_analysis_record(current_user.id, record_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to delete this analysis.") from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found.")


@router.get("/dashboard/stats", response_model=DashboardStatsResponse, summary="Get aggregate stats")
def get_dashboard_stats(current_user: CurrentUser = Depends(get_current_user)) -> DashboardStatsResponse:
    try:
        stats = history_service.get_dashboard_stats(current_user.id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Failed to load dashboard stats. Ensure SUPABASE_URL/SUPABASE_KEY are configured.",
        ) from exc
    return DashboardStatsResponse(**stats)


@router.get(
    "/dashboard/recent-activity",
    response_model=AnalysisListResponse,
    summary="Get the current user's most recent analyses",
)
def get_recent_activity(
    limit: int = Query(default=8, ge=1, le=50),
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalysisListResponse:
    try:
        records = history_service.get_recent_activity(current_user.id, limit=limit)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to load recent activity.") from exc

    return AnalysisListResponse(
        items=[AnalysisRecord(**record) for record in records],
        total=len(records),
        limit=limit,
        offset=0,
    )
