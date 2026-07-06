# syntax=docker/dockerfile:1

# SafePrompt AI backend — FastAPI + ML detectors (Milestones 7-8), talking
# exclusively to Supabase (no local database in this image at all — see
# app/db/supabase_client.py). Run backend/supabase/schema.sql once against
# your Supabase project's SQL Editor before pointing this container at it;
# it is not run automatically anywhere in this Dockerfile or at app startup.
#
# Image size note: requirements.txt unconditionally installs torch,
# transformers, sentence-transformers, and detoxify (~2-3 GB combined),
# even though ENABLE_ML_DETECTORS=False at runtime skips loading them —
# there's no separate "lite" requirements file today. Expect this build
# (and `docker compose build`) to take several minutes.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# curl: used by the HEALTHCHECK below.
# build-essential: covers the rare native-extension wheel (e.g.
# tokenizers/sentencepiece) without a prebuilt wheel for this exact base
# image/architecture — pip falls back to compiling from source otherwise.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copied and installed before the rest of the app so this layer is only
# rebuilt when dependencies actually change, not on every code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Runs as a non-root user in production, per standard container hardening
# practice — the app never needs root privileges. REPORTS_DIR (Settings,
# app/core/config.py) resolves to /app/reports at runtime; created and
# owned by appuser up front so PDF generation (app/services/report_service.py)
# doesn't hit a permissions error on first use. Mount a volume at
# /app/reports (see docker-compose.yml) if you want generated reports to
# survive a container recreate.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/reports \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Single worker by default — fine for the traffic this app is likely to
# see and keeps memory usage (torch + transformers models, if
# ENABLE_ML_DETECTORS=True) predictable. Scale by running multiple
# container replicas behind a load balancer rather than multiple uvicorn
# workers in one container, so each replica's memory footprint stays the
# same and you can scale/restart them independently.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
