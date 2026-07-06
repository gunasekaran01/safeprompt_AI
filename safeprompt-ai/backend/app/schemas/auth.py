"""Schemas describing the currently authenticated user."""

from typing import Optional

from pydantic import BaseModel


class CurrentUser(BaseModel):
    """Minimal identity extracted from a validated Supabase JWT."""

    id: str
    email: Optional[str] = None
