"""Schemas for /api/history and /api/dashboard/* endpoints."""

from datetime import datetime
from typing import List, Optional

from app.schemas.base import CamelCaseModel


class AnalysisRecord(CamelCaseModel):
    id: str
    user_id: str
    prompt: str
    injection_detected: bool
    injection_confidence: float
    injection_reason: str
    toxicity_detected: bool
    toxicity_category: str
    toxicity_confidence: float
    toxicity_explanation: str
    safety_score: float
    risk_level: str
    recommendation: str
    reasoning: str
    created_at: datetime


class AnalysisListResponse(CamelCaseModel):
    items: List[AnalysisRecord]
    total: int
    limit: int
    offset: int


class DashboardStatsResponse(CamelCaseModel):
    total_analyses: int
    safe_prompts: int
    unsafe_prompts: int
    injection_attempts: int
    toxic_prompts: int
    average_safety_score: float
    safe_count: int
    low_count: int
    medium_count: int
    high_count: int
    critical_count: int


class HistoryQueryParams(CamelCaseModel):
    search: Optional[str] = None
    risk_level: Optional[str] = None
    limit: int = 20
    offset: int = 0


# Legacy alias kept for compatibility with older route modules.
HistoryResponse = AnalysisListResponse
