"""Schemas for the dashboard chart endpoint (GET /api/dashboard/charts).

Extends CamelCaseModel (see schemas/base.py) so the JSON matches every
other real endpoint (history, dashboard stats, analyze) and needs no
extra frontend-side field mapping — DashboardCharts.jsx consumes these
fields directly (e.g. `point.averageScore`, `row.riskLevel`,
`detectionBreakdown.injectionOnly`).
"""

from typing import List

from app.schemas.base import CamelCaseModel


class ScoreTrendPoint(CamelCaseModel):
    date: str
    average_score: float
    count: int


class RiskLevelCount(CamelCaseModel):
    risk_level: str
    count: int


class DetectionBreakdown(CamelCaseModel):
    injection_only: int
    toxicity_only: int
    both: int
    none: int


class ChartDataResponse(CamelCaseModel):
    score_trend: List[ScoreTrendPoint]
    risk_level_distribution: List[RiskLevelCount]
    detection_breakdown: DetectionBreakdown
