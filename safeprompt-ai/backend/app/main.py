"""
SafePrompt AI backend entrypoint.

Application bootstrap: CORS configuration, router registration, a health
check endpoint, and a startup check that warns (without crashing) if
Supabase credentials are missing, since several endpoints depend on them.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.charts import router as charts_router
from app.api.history import router as history_router
from app.api.profile import router as profile_router
from app.api.reports import router as reports_router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not settings.is_supabase_configured:
        logger.warning(
            "SUPABASE_URL / SUPABASE_KEY are not set. Authentication (/api/auth/me) "
            "and any database-backed endpoints will return errors until these are "
            "configured. See backend/.env.example."
        )
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Prompt Injection and Toxicity Detection Platform",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(history_router)
app.include_router(charts_router)
app.include_router(reports_router)


@app.get("/api/health", tags=["System"])
def health_check() -> dict:
    """
    Simple health check used by the frontend, Docker healthchecks, and CI
    to confirm the API process is up and correctly configured.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "supabase_configured": settings.is_supabase_configured,
    }


@app.get("/api", tags=["System"])
def root() -> dict:
    """Root API metadata endpoint."""
    return {
        "message": "Welcome to the SafePrompt AI API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
