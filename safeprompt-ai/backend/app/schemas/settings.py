"""
Schemas for GET/PATCH /api/settings — the server-synced counterpart to
the preferences previously kept only in the browser's localStorage (see
frontend/src/pages/SettingsPage.jsx and useLocalStorage.js). Backed by
the `user_settings` table in supabase/schema.sql.

Uses CamelCaseModel so the JSON matches the rest of the newer,
frontend-facing endpoints (profiles, charts) -- theme, compactMode,
autoAnalyzeOnPaste, updatedAt.
"""

from typing import Literal, Optional

from app.schemas.base import CamelCaseModel

Theme = Literal["light", "dark", "system"]


class SettingsResponse(CamelCaseModel):
    theme: Theme
    compact_mode: bool
    auto_analyze_on_paste: bool
    updated_at: str


class SettingsUpdateRequest(CamelCaseModel):
    """All fields optional -- PATCH applies only what's provided."""

    theme: Optional[Theme] = None
    compact_mode: Optional[bool] = None
    auto_analyze_on_paste: Optional[bool] = None
