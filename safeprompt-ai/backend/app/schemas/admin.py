"""Pydantic schemas for the admin routes (app/api/routes/admin.py)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RiskLevelCount(BaseModel):
    """Count of analyses at a given risk level, for the admin overview's distribution chart."""

    risk_level: str
    count: int


class AdminOverviewResponse(BaseModel):
    """Response body for GET /api/admin/overview: platform-wide totals."""

    total_users: int
    total_analyses: int
    total_reports: int
    safe_prompts: int
    unsafe_prompts: int
    injection_attempts: int
    toxic_prompts: int
    average_safety_score: float
    risk_level_distribution: List[RiskLevelCount]


class AdminUserSummary(BaseModel):
    """A single row in GET /api/admin/users."""

    id: str
    email: str
    name: Optional[str] = None
    is_admin: bool
    created_at: datetime
    analyses_count: int


class AdminUsersResponse(BaseModel):
    """Response body for GET /api/admin/users."""

    users: List[AdminUserSummary]
    total: int
