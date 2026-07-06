"""
Tests for authentication: the get_current_user dependency and the
protected /api/auth/me endpoint.

Since these tests run without network access to a real Supabase project,
the Supabase client's `auth.get_user()` call is mocked to simulate valid,
invalid, and misconfigured scenarios.
"""

from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _mock_supabase_client(user_id="user-123", email="test@example.com", raise_error=False):
    mock_client = SimpleNamespace()

    def get_user(_token):
        if raise_error:
            raise Exception("invalid JWT")
        return SimpleNamespace(user=SimpleNamespace(id=user_id, email=email))

    mock_client.auth = SimpleNamespace(get_user=get_user)
    return mock_client


def test_me_without_authorization_header_returns_401():
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_valid_token_returns_current_user():
    with patch("app.core.security.get_supabase_client", return_value=_mock_supabase_client()):
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer valid-token"})
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "user-123"
    assert body["email"] == "test@example.com"


def test_me_with_invalid_token_returns_401():
    with patch(
        "app.core.security.get_supabase_client",
        return_value=_mock_supabase_client(raise_error=True),
    ):
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer bad-token"})
    assert response.status_code == 401


def test_me_when_supabase_not_configured_returns_500():
    def raise_runtime_error():
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")

    with patch("app.core.security.get_supabase_client", side_effect=raise_runtime_error):
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer any-token"})
    assert response.status_code == 500
