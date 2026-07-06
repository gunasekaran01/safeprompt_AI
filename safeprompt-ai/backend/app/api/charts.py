"""
Dashboard chart routes.

New route module wired against the currently-active data path
(app/services/dashboard_charts_service.py), not the broken
app/api/routes/stats.py. Mounted directly in main.py alongside the other
app/api/*.py routers, next to /api/dashboard/stats and
/api/dashboard/recent-activity (app/api/history.py).

GET /api/dashboard/charts -> the three Chart.js datasets consumed by
frontend/src/components/Dashboard/DashboardCharts.jsx.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.charts import ChartDataResponse
from app.services import dashboard_charts_service

router = APIRouter(prefix="/api", tags=["Charts"])


@router.get(
    "/dashboard/charts",
    response_model=ChartDataResponse,
    summary="Get chart datasets for the dashboard",
)
def get_dashboard_charts(
    days: int = Query(default=14, ge=1, le=90),
    current_user: CurrentUser = Depends(get_current_user),
) -> ChartDataResponse:
    try:
        return dashboard_charts_service.compute_chart_data(user_id=current_user.id, days=days)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to load chart data.") from exc
