"""
Admin dashboard aggregation service.

Mirrors app/services/stats_service.py's approach (fetch rows, aggregate
in Python — Supabase's REST API has no arbitrary GROUP BY without a
Postgres RPC function) but computes platform-wide totals across every
user instead of one user's own data, via app/db/admin_crud.py's
admin-scoped queries.
"""

from collections import defaultdict
from typing import Any, Dict, List

from supabase import Client

from app.api.deps import is_admin_email
from app.db import admin_crud
from app.schemas.admin import (
    AdminOverviewResponse,
    AdminUserSummary,
    AdminUsersResponse,
    RiskLevelCount,
)

RISK_LEVEL_ORDER = ("safe", "low", "medium", "high", "critical")


def compute_admin_overview(client: Client) -> AdminOverviewResponse:
    """Aggregate platform-wide totals for the admin dashboard's stat cards."""
    profiles = admin_crud.list_all_profiles(client)
    analyses = admin_crud.list_all_analyses_raw(client)
    total_reports = admin_crud.count_all_reports(client)

    total_analyses = len(analyses)

    risk_counts: Dict[str, int] = defaultdict(int)
    for row in analyses:
        risk_counts[row.get("risk_level", "safe")] += 1
    risk_distribution = [
        RiskLevelCount(risk_level=level, count=risk_counts.get(level, 0))
        for level in RISK_LEVEL_ORDER
    ]

    safe = sum(1 for row in analyses if row.get("risk_level") in ("safe", "low"))
    injection = sum(1 for row in analyses if row.get("injection_detected"))
    toxic = sum(1 for row in analyses if row.get("toxicity_detected"))
    average_score = (
        round(sum(row.get("safety_score", 0) for row in analyses) / total_analyses, 1)
        if total_analyses
        else 0.0
    )

    return AdminOverviewResponse(
        total_users=len(profiles),
        total_analyses=total_analyses,
        total_reports=total_reports,
        safe_prompts=safe,
        unsafe_prompts=total_analyses - safe,
        injection_attempts=injection,
        toxic_prompts=toxic,
        average_safety_score=average_score,
        risk_level_distribution=risk_distribution,
    )


def list_users_with_counts(client: Client) -> AdminUsersResponse:
    """
    Returns every user's profile plus how many analyses they've run, for
    the admin dashboard's user table.
    """
    profiles: List[Dict[str, Any]] = admin_crud.list_all_profiles(client)
    analyses: List[Dict[str, Any]] = admin_crud.list_all_analyses_raw(client)

    counts_by_user: Dict[str, int] = defaultdict(int)
    for row in analyses:
        user_id = row.get("user_id")
        if user_id:
            counts_by_user[user_id] += 1

    users = [
        AdminUserSummary(
            id=profile["id"],
            email=profile["email"],
            name=profile.get("name"),
            is_admin=is_admin_email(profile.get("email")),
            created_at=profile["created_at"],
            analyses_count=counts_by_user.get(profile["id"], 0),
        )
        for profile in profiles
    ]

    return AdminUsersResponse(users=users, total=len(users))
