"""
Tests for the profile service and GET/PATCH /api/profile.

Uses FastAPI's dependency_overrides to stub get_current_user (so we don't
need a real JWT), and mocks profile_service's Supabase client to simulate
table query/update results without a live database.
"""

from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.main import app
from app.schemas.auth import CurrentUser

client = TestClient(app)

FAKE_USER = CurrentUser(id="user-123", email="test@example.com")


class _MockQueryBuilder:
    """Minimal stand-in for supabase-py's fluent query builder."""

    def __init__(self, data):
        self._data = data

    def select(self, *_args, **_kwargs):
        return self

    def update(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self._data)


def _mock_client(data):
    return SimpleNamespace(table=lambda _name: _MockQueryBuilder(data))


def _override_auth():
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER


def _clear_auth_override():
    app.dependency_overrides.pop(get_current_user, None)


def test_get_profile_without_token_returns_401():
    response = client.get("/api/profile")
    assert response.status_code == 401


def test_get_profile_returns_current_users_profile():
    profile_row = {
        "id": "user-123",
        "name": "Ada Lovelace",
        "email": "test@example.com",
        "avatar_url": None,
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-01T00:00:00+00:00",
    }
    _override_auth()
    try:
        with patch(
            "app.services.profile_service.get_supabase_client",
            return_value=_mock_client([profile_row]),
        ):
            response = client.get("/api/profile")
    finally:
        _clear_auth_override()

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "user-123"
    assert body["name"] == "Ada Lovelace"
    assert body["avatarUrl"] is None


def test_get_profile_not_found_returns_404():
    _override_auth()
    try:
        with patch(
            "app.services.profile_service.get_supabase_client",
            return_value=_mock_client([]),
        ):
            response = client.get("/api/profile")
    finally:
        _clear_auth_override()

    assert response.status_code == 404


def test_update_profile_applies_partial_update():
    updated_row = {
        "id": "user-123",
        "name": "New Name",
        "email": "test@example.com",
        "avatar_url": "https://example.com/avatar.png",
        "created_at": "2026-01-01T00:00:00+00:00",
        "updated_at": "2026-01-02T00:00:00+00:00",
    }
    _override_auth()
    try:
        with patch(
            "app.services.profile_service.get_supabase_client",
            return_value=_mock_client([updated_row]),
        ):
            response = client.patch("/api/profile", json={"name": "New Name"})
    finally:
        _clear_auth_override()

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "New Name"
    assert body["avatarUrl"] == "https://example.com/avatar.png"


def test_update_profile_without_token_returns_401():
    response = client.patch("/api/profile", json={"name": "New Name"})
    assert response.status_code == 401
