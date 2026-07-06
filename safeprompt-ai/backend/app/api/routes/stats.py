"""
Dashboard stats/chart routes — Milestone 12.

Wraps app/services/stats_service.py, which aggregates the persisted
Supabase `analyses` rows into the dashboard overview counters and the
three Chart.js datasets (score trend, risk-level distribution, detection
breakdown). All aggregation happens in Python over rows fetched via
app/db/crud.list_all_analyses(); see stats_service.py's module docstring
for why (PostgREST has no arbitrary GROUP BY without a Postgres RPC
function).

SaaS Phase 4: every route requires authentication, and every aggregate
is computed only over the authenticated user's own analyses.

Exposes three routes:
- GET /api/stats            -> combined overview + charts in one response
  (convenience endpoint for callers that want everything in one request).
- GET /api/stats/overview    -> just the stat-card counters.
- GET /api/stats/charts      -> just the three chart datasets.
"""

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, get_current_user
from app.schemas.stats import ChartDataResponse, StatsOverview
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["Stats"])


class StatsCombinedResponse(BaseModel):
    """Response body for GET /api/stats."""

    overview: StatsOverview
    charts: ChartDataResponse = Field(..., description="Chart datasets over the trailing `days` window.")


@router.get("", response_model=StatsCombinedResponse, summary="Combined dashboard overview + charts")
def get_stats(
    days: int = Query(14, ge=1, le=90, description="Number of days to include in the score trend."),
    current_user: CurrentUser = Depends(get_current_user),
) -> StatsCombinedResponse:
    """Returns the authenticated user's overview counters and chart datasets in a single call."""
    return StatsCombinedResponse(
        overview=stats_service.compute_overview(user_id=current_user.id),
        charts=stats_service.compute_chart_data(user_id=current_user.id, days=days),
    )


@router.get("/overview", response_model=StatsOverview, summary="Aggregate dashboard stats")
def get_overview(current_user: CurrentUser = Depends(get_current_user)) -> StatsOverview:
    """Returns the authenticated user's total/safe/unsafe/injection/toxic counts and average score."""
    return stats_service.compute_overview(user_id=current_user.id)


@router.get("/charts", response_model=ChartDataResponse, summary="Chart datasets for the dashboard")
def get_charts(
    days: int = Query(14, ge=1, le=90, description="Number of days to include in the score trend."),
    current_user: CurrentUser = Depends(get_current_user),
) -> ChartDataResponse:
    """Returns the authenticated user's score trend, risk-level distribution, and detection breakdown datasets."""
    return stats_service.compute_chart_data(user_id=current_user.id, days=days)
