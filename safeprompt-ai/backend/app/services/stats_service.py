"""
Dashboard stats/aggregation service — Milestone 12.

Supabase's REST API (PostgREST) doesn't expose arbitrary GROUP BY
aggregation without writing a custom Postgres function and calling it
via RPC. For a project at this scale, the simpler and equally correct
trade-off is: fetch the (capped) set of recent analyses once via
app/db/crud.list_all_analyses(), then aggregate in Python. If the
dataset grows large enough for this to matter, the fetch-and-aggregate
calls below are the only things that would need to move to a Postgres
RPC function — the route layer (app/api/routes/stats.py) and response
schemas wouldn't change.
"""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List

from app.db import crud
from app.schemas.analysis import AnalyzeResponse
from app.schemas.stats import (
    ChartDataResponse,
    DetectionBreakdown,
    RiskLevelCount,
    ScoreTrendPoint,
    StatsOverview,
)

# Upper bound on how many rows we pull from Supabase to compute stats
# over. Keeps this fast and bounded even if the table grows large;
# increase if you need stats over a bigger history window.
MAX_RECORDS_FOR_STATS = 5000

RISK_LEVEL_ORDER = ("safe", "low", "medium", "high", "critical")


def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def compute_overview(user_id: str) -> StatsOverview:
    """Aggregate counts for the dashboard's top stat-card row, scoped to `user_id`."""
    records: List[AnalyzeResponse] = crud.list_all_analyses(user_id=user_id, limit=MAX_RECORDS_FOR_STATS)
    total = len(records)

    if total == 0:
        return StatsOverview(
            total_analyses=0,
            safe_prompts=0,
            unsafe_prompts=0,
            injection_attempts=0,
            toxic_prompts=0,
            average_safety_score=0.0,
        )

    safe = sum(1 for r in records if r.risk_level in ("safe", "low"))
    injection = sum(1 for r in records if r.injection_detected)
    toxic = sum(1 for r in records if r.toxicity_detected)
    average_score = sum(r.score for r in records) / total

    return StatsOverview(
        total_analyses=total,
        safe_prompts=safe,
        unsafe_prompts=total - safe,
        injection_attempts=injection,
        toxic_prompts=toxic,
        average_safety_score=round(average_score, 1),
    )


def compute_chart_data(user_id: str, days: int = 14) -> ChartDataResponse:
    """
    Builds the three Milestone 12 chart datasets, scoped to `user_id`: a
    daily average-score trend for the last `days` days, a risk-level
    distribution, and an injection/toxicity detection breakdown.
    """
    records: List[AnalyzeResponse] = crud.list_all_analyses(user_id=user_id, limit=MAX_RECORDS_FOR_STATS)

    # --- Risk level distribution -------------------------------------
    risk_counts: dict[str, int] = defaultdict(int)
    for r in records:
        risk_counts[r.risk_level] += 1
    risk_distribution = [
        RiskLevelCount(risk_level=level, count=risk_counts.get(level, 0))
        for level in RISK_LEVEL_ORDER
    ]

    # --- Detection breakdown -------------------------------------------
    injection_only = sum(1 for r in records if r.injection_detected and not r.toxicity_detected)
    toxicity_only = sum(1 for r in records if r.toxicity_detected and not r.injection_detected)
    both = sum(1 for r in records if r.injection_detected and r.toxicity_detected)
    neither = sum(1 for r in records if not r.injection_detected and not r.toxicity_detected)
    breakdown = DetectionBreakdown(
        injection_only=injection_only,
        toxicity_only=toxicity_only,
        both=both,
        none=neither,
    )

    # --- Score trend, last `days` days, average score per day ---------
    today = _as_utc(datetime.now(timezone.utc))
    start_date = (today - timedelta(days=days - 1)).date()

    buckets: dict[str, List[float]] = defaultdict(list)
    for r in records:
        ts = _as_utc(r.timestamp)
        if ts.date() < start_date:
            continue
        buckets[ts.date().isoformat()].append(r.score)

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
