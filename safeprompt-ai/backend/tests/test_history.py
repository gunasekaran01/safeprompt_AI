"""
Tests for /api/history and /api/dashboard/* endpoints.

Uses dependency_overrides to stub authentication and mocks the Supabase
query builder to simulate results without a live database. Specifically
verifies that user_id scoping is applied on every query — the actual
enforcement layer given the backend uses the Supabase service role key
(which bypasses RLS).
"""

from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.main import app
from app.schemas.auth import CurrentUser

client = TestClient(app)

FAKE_USER = CurrentUser(id="user-123", email="test@example.com")

SAMPLE_RECORD = {
    "id": "rec-1",
    "user_id": "user-123",
    "prompt": "Summarize this.",
    "injection_detected": False,
    "injection_confidence": 0.95,
    "injection_reason": "No known prompt injection patterns were found in the input.",
    "toxicity_detected": False,
    "toxicity_category": "none",
    "toxicity_confidence": 0.9,
    "toxicity_explanation": "No toxic language patterns were found in the input.",
    "safety_score": 96.0,
    "risk_level": "safe",
    "recommendation": "Safe to process.",
    "reasoning": "Clean.",
    "created_at": "2026-01-01T00:00:00+00:00",
}

SAMPLE_STATS = {
    "user_id": "user-123",
    "total_analyses": 10,
    "safe_prompts": 8,
    "unsafe_prompts": 2,
    "injection_attempts": 1,
    "toxic_prompts": 1,
    "average_safety_score": 82.5,
    "safe_count": 7,
    "low_count": 1,
    "medium_count": 1,
    "high_count": 1,
    "critical_count": 0,
}


class _RecordingQueryBuilder:
    """Mock query builder that records every .eq() call so tests can
    assert the query was actually scoped by user_id."""

    def __init__(self, data, count=None):
        self._data = data
        self._count = count
        self.eq_calls = []

    def select(self, *_args, **_kwargs):
        return self

    def insert(self, *_args, **_kwargs):
        return self

    def delete(self, *_args, **_kwargs):
        return self

    def eq(self, field, value):
        self.eq_calls.append((field, value))
        return self

    def ilike(self, *_args, **_kwargs):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def range(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self._data, count=self._count)


def _override_auth():
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER


def _clear_auth_override():
    app.dependency_overrides.pop(get_current_user, None)


def test_history_without_token_returns_401():
    response = client.get("/api/history")
    assert response.status_code == 401


def test_history_returns_only_current_users_records_and_is_scoped_by_user_id():
    builder = _RecordingQueryBuilder([SAMPLE_RECORD], count=1)
    _override_auth()
    try:
        with patch(
            "app.services.history_service.get_supabase_client",
            return_value=SimpleNamespace(table=lambda _name: builder),
        ):
            response = client.get("/api/history")
    finally:
        _clear_auth_override()

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["userId"] == "user-123"
    # The critical assertion: every query was scoped by this user's id.
    assert ("user_id", "user-123") in builder.eq_calls


def test_history_rejects_invalid_risk_level():
    _override_auth()
    try:
        response = client.get("/api/history", params={"risk_level": "not-a-real-level"})
    finally:
        _clear_auth_override()
    assert response.status_code == 422


def test_delete_history_item_scoped_to_user():
    builder = _RecordingQueryBuilder([SAMPLE_RECORD])
    _override_auth()
    try:
        with patch(
            "app.services.history_service.get_supabase_client",
            return_value=SimpleNamespace(table=lambda _name: builder),
        ):
            response = client.delete("/api/history/rec-1")
    finally:
        _clear_auth_override()

    assert response.status_code == 204
    assert ("user_id", "user-123") in builder.eq_calls
    assert ("id", "rec-1") in builder.eq_calls


def test_delete_nonexistent_history_item_returns_404():
    builder = _RecordingQueryBuilder([])
    _override_auth()
    try:
        with patch(
            "app.services.history_service.get_supabase_client",
            return_value=SimpleNamespace(table=lambda _name: builder),
        ):
            response = client.delete("/api/history/does-not-exist")
    finally:
        _clear_auth_override()
    assert response.status_code == 404


def test_dashboard_stats_scoped_to_user():
    """
    Exercises the real-Supabase branch of history_service.get_dashboard_stats
    (reading the pre-aggregated analyses_stats view), not the local-store
    branch -- conftest.py force-sets USE_LOCAL_DATA_STORE=True for every
    test (so /api/analyze etc. run fully offline), which would otherwise
    make get_dashboard_stats take its local-computation branch instead and
    treat SAMPLE_STATS as a single raw analysis row rather than the
    pre-aggregated view row it actually represents. Monkeypatching the
    setting just for this test lets it verify the branch it's actually
    named for.
    """
    from app.core.config import get_settings

    builder = _RecordingQueryBuilder([SAMPLE_STATS])
    _override_auth()
    try:
        with (
            patch("app.services.history_service.get_supabase_client",
                  return_value=SimpleNamespace(table=lambda _name: builder)),
            patch.object(get_settings(), "USE_LOCAL_DATA_STORE", False),
        ):
            response = client.get("/api/dashboard/stats")
    finally:
        _clear_auth_override()

    assert response.status_code == 200
    body = response.json()
    assert body["totalAnalyses"] == 10
    assert body["averageSafetyScore"] == 82.5
    assert ("user_id", "user-123") in builder.eq_calls


def test_dashboard_stats_without_token_returns_401():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 401


def test_recent_activity_scoped_to_user():
    builder = _RecordingQueryBuilder([SAMPLE_RECORD])
    _override_auth()
    try:
        with patch(
            "app.services.history_service.get_supabase_client",
            return_value=SimpleNamespace(table=lambda _name: builder),
        ):
            response = client.get("/api/dashboard/recent-activity")
    finally:
        _clear_auth_override()

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert ("user_id", "user-123") in builder.eq_calls
