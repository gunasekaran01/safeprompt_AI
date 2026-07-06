"""
Analysis history routes — Milestone 11.

Exposes the persisted analyses (Supabase `analyses` table, written by
POST /api/analyze) for the frontend HistoryPage: a paginated, filterable
listing, a single-record lookup, and delete.

Filtering supports: risk_level (exact match), search (case-insensitive
substring over the prompt text), and injection_only/toxicity_only flags.
All filtering happens in app/db/crud.py via Supabase query params, not
in this route module.

SaaS Phase 4: every route requires authentication and scopes its query
to the authenticated user's own `user_id` — a user can never list, read,
or delete another user's analyses, and a record that exists but belongs
to someone else returns 404, identically to a record that doesn't exist
at all.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, get_current_user
from app.db import crud
from app.schemas.analysis import AnalyzeResponse
from app.schemas.history import HistoryResponse

router = APIRouter(prefix="/history", tags=["History"])

VALID_RISK_LEVELS = {"safe", "low", "medium", "high", "critical"}


@router.get("", response_model=HistoryResponse, summary="List past analyses")
def get_history(
    limit: int = Query(20, ge=1, le=100, description="Page size."),
    offset: int = Query(0, ge=0, description="Number of records to skip."),
    risk_level: Optional[str] = Query(
        None, description="Filter by exact risk level: safe, low, medium, high, critical."
    ),
    search: Optional[str] = Query(
        None, min_length=1, max_length=200, description="Case-insensitive substring search over the prompt text."
    ),
    injection_only: bool = Query(False, description="Only return analyses that flagged injection."),
    toxicity_only: bool = Query(False, description="Only return analyses that flagged toxicity."),
    current_user: CurrentUser = Depends(get_current_user),
) -> HistoryResponse:
    """Returns a paginated, filtered page of the authenticated user's own past analyses, newest first."""
    if risk_level and risk_level not in VALID_RISK_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"risk_level must be one of {sorted(VALID_RISK_LEVELS)}",
        )

    filters = dict(
        risk_level=risk_level,
        search=search,
        injection_only=injection_only,
        toxicity_only=toxicity_only,
    )
    items = crud.list_analyses(user_id=current_user.id, limit=limit, offset=offset, **filters)
    total = crud.count_analyses(user_id=current_user.id, **filters)
    return HistoryResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{analysis_id}", response_model=AnalyzeResponse, summary="Get a single analysis by id")
def get_history_item(
    analysis_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalyzeResponse:
    """Returns one of the authenticated user's own persisted analyses, or 404 if it doesn't exist (or isn't theirs)."""
    record = crud.get_analysis(analysis_id, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return record


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a single analysis",
)
def delete_history_item(
    analysis_id: str,
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    """Deletes one of the authenticated user's own persisted analyses, or 404 if it doesn't exist (or isn't theirs)."""
    deleted = crud.delete_analysis(analysis_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
