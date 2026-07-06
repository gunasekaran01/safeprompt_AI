"""
Dashboard chart aggregation.

New module, built against the same table/fields that
app/services/history_service.py already reads and writes (the
currently-active data path), rather than the broken
app/services/stats_service.py (which depends on app/db/crud.py and a
schema class, AnalyzeResponse, that no longer exists in this codebase).

Aggregates the authenticated user's own `analyses` rows into three
Chart.js-ready datasets: a daily average-score trend, a risk-level
distribution, and an injection/toxicity detection breakdown.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.db.supabase_client import get_supabase_client
from app.schemas.charts import (
    ChartDataResponse,
    DetectionBreakdown,
    RiskLevelCount,
    ScoreTrendPoint,
)

ANALYSES_TABLE = "analyses"
RISK_LEVEL_ORDER = ("safe", "low", "medium", "high", "critical")

# Upper bound on rows pulled per computation — keeps this fast and
# bounded even if a user's history grows large.
MAX_RECORDS_FOR_STATS = 5000


def _parse_date(value: Any) -> Optional[datetime.date]:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def compute_chart_data(user_id: str, days: int = 14) -> ChartDataResponse:
    client = get_supabase_client()
    response = (
        client.table(ANALYSES_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(MAX_RECORDS_FOR_STATS)
        .execute()
    )
    rows: List[Dict[str, Any]] = response.data or []

    # --- Risk level distribution -------------------------------------
    risk_counts: dict = defaultdict(int)
    for row in rows:
        risk_counts[row.get("risk_level", "medium")] += 1
    risk_distribution = [
        RiskLevelCount(risk_level=level, count=risk_counts.get(level, 0))
        for level in RISK_LEVEL_ORDER
    ]

    # --- Detection breakdown ------------------------------------------
    injection_only = sum(
        1 for r in rows if r.get("injection_detected") and not r.get("toxicity_detected")
    )
    toxicity_only = sum(
        1 for r in rows if r.get("toxicity_detected") and not r.get("injection_detected")
    )
    both = sum(1 for r in rows if r.get("injection_detected") and r.get("toxicity_detected"))
    neither = sum(
        1 for r in rows if not r.get("injection_detected") and not r.get("toxicity_detected")
    )
    breakdown = DetectionBreakdown(
        injection_only=injection_only,
        toxicity_only=toxicity_only,
        both=both,
        none=neither,
    )

    # --- Score trend, last `days` days, average score per day ---------
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=days - 1)

    buckets: dict = defaultdict(list)
    for row in rows:
        day = _parse_date(row.get("created_at"))
        if day is None or day < start_date:
            continue
        buckets[day.isoformat()].append(row.get("safety_score", 0))

    trend: List[ScoreTrendPoint] = []
    for offset in range(days):
        day = start_date + timedelta(days=offset)
        day_key = day.isoformat()
        scores = buckets.get(day_key, [])
        average = round(sum(scores) / len(scores), 1) if scores else 0.0
        trend.append(ScoreTrendPoint(date=day_key, average_score=average, count=len(scores)))

    return ChartDataResponse(
        score_trend=trend,
        risk_level_distribution=risk_distribution,
        detection_breakdown=breakdown,
    )
