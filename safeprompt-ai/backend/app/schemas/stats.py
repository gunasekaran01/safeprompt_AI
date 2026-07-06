"""
Pydantic schemas for the Milestone 12 Stats/Charts endpoints.

`StatsOverview` mirrors the shape the frontend has been rendering from
mock data since Milestone 4 (see frontend/src/services/mockData.js ->
MOCK_STATS), so DashboardPage's StatsGrid needs no changes beyond
swapping its data source. `ChartDataResponse` is new: it feeds the three
Chart.js visualizations built in Milestone 12
(frontend/src/components/Dashboard/charts/*).
"""

from typing import List

from pydantic import BaseModel, Field


class StatsOverview(BaseModel):
    """Response body for GET /api/stats/overview."""

    total_analyses: int
    safe_prompts: int
    unsafe_prompts: int
    injection_attempts: int
    toxic_prompts: int
    average_safety_score: float


class ScoreTrendPoint(BaseModel):
    """A single day's average safety score, for the score trend line chart."""

    date: str = Field(..., description="ISO date (YYYY-MM-DD).")
    average_score: float
    count: int = Field(..., description="Number of analyses that day.")


class RiskLevelCount(BaseModel):
    """Count of analyses at a given risk level, for the distribution chart."""

    risk_level: str
    count: int


class DetectionBreakdown(BaseModel):
    """
    Counts of analyses by which detector(s) fired, for the detection type
    chart: injection only, toxicity only, both, or neither.
    """

    injection_only: int
    toxicity_only: int
    both: int
    none: int


class ChartDataResponse(BaseModel):
    """Response body for GET /api/stats/charts."""

    score_trend: List[ScoreTrendPoint] = Field(default_factory=list)
    risk_level_distribution: List[RiskLevelCount] = Field(default_factory=list)
    detection_breakdown: DetectionBreakdown
