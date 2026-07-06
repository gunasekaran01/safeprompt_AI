"""Pydantic schemas for authentication.

Two response shapes are used across the auth-related routes:

- `CurrentUser`: the minimal id/email pair used internally by
  app/core/security.py's `get_current_user` dependency, and consumed as
  a type hint by every route that just needs to know *who* is calling
  (app/api/analysis.py, app/api/history.py, app/api/charts.py,
  app/api/reports.py).
- `CurrentUserResponse`: the richer response body for GET /api/auth/me
  (app/api/routes/auth.py), which additionally includes `is_admin` —
  computed server-side (app.api.deps.is_admin_email against
  Settings.admin_emails_list) rather than trusted from the client. This
  is what frontend/src/utils/AuthContext.jsx fetches so `isAdmin` is
  never just a client-side email comparison that could be spoofed or
  drift out of sync with the backend's actual admin check.
"""

from typing import Optional

from pydantic import BaseModel


class CurrentUser(BaseModel):
    """Minimal identity extracted from a validated Supabase JWT."""

    id: str
    email: Optional[str] = None


class CurrentUserResponse(BaseModel):
    """Response body for GET /api/auth/me."""

    id: str
    email: Optional[str] = None
    is_admin: bool = False
