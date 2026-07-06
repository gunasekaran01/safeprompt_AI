"""
Authentication dependency.

Validates the Supabase-issued JWT sent by the frontend as a Bearer token
and resolves it to the current user. Validation is delegated to
Supabase itself (via `client.auth.get_user(token)`), so token expiry,
signature, and revocation are all handled correctly without the backend
needing to manage its own JWT secret/verification logic.

Usage:
    @router.get("/api/protected-thing")
    def handler(current_user: CurrentUser = Depends(get_current_user)):
        ...
"""

import logging

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.supabase_client import get_supabase_client
from app.schemas.auth import CurrentUser

logger = logging.getLogger(__name__)

# auto_error=False so we can return a consistent 401 body ourselves
# (rather than FastAPI's default) when the header is missing entirely.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> CurrentUser:
    """
    Resolves the current authenticated user from a Supabase JWT.

    Raises HTTP 401 if the Authorization header is missing, malformed,
    or the token is invalid/expired.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token. Include 'Authorization: Bearer <token>'.",
        )

    token = credentials.credentials

    try:
        client = get_supabase_client()
        response = client.auth.get_user(token)
    except RuntimeError as exc:
        # Supabase isn't configured at all — a server misconfiguration,
        # not a client auth failure, so surface it as a 500 instead of 401.
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - any token validation failure
        logger.info("JWT validation failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.") from exc

    user = getattr(response, "user", None)
    if user is None or not getattr(user, "id", None):
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")

    return CurrentUser(id=user.id, email=getattr(user, "email", None))
