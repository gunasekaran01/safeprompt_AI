"""Schemas for GET/PATCH /api/profile."""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import Field

from app.schemas.base import CamelCaseModel


class ProfileResponse(CamelCaseModel):
    id: str
    name: Optional[str] = None
    email: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProfileUpdateRequest(CamelCaseModel):
    """Partial update — omitted/None fields are left unchanged."""

    name: Optional[Annotated[str, Field(max_length=200)]] = None
    avatar_url: Optional[Annotated[str, Field(max_length=2000)]] = None
