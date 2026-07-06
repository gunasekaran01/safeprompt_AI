"""
Aggregate API router.

Combines all route modules under app/api/routes/ into a single router
mounted at /api in main.py. New route modules register themselves here
rather than in main.py, keeping main.py focused on application bootstrap
only.

Mounted routers:
- analysis  (Milestone 6)  -> POST /api/analyze
- history   (Milestone 11) -> GET/DELETE /api/history...
- stats     (Milestone 12) -> GET /api/stats...
- reports   (Milestone 13) -> GET /api/reports/{analysis_id}
- auth      (SaaS Phase 1) -> GET /api/auth/me
- profiles  (SaaS Phase 2) -> GET/PATCH /api/profiles/me
- admin                    -> GET /api/admin/overview, GET/DELETE /api/admin/users...
"""

from fastapi import APIRouter

from app.api.routes import admin, analysis, auth, history, profiles, reports, stats

api_router = APIRouter()
api_router.include_router(analysis.router)
api_router.include_router(history.router)
api_router.include_router(stats.router)
api_router.include_router(reports.router)
api_router.include_router(auth.router)
api_router.include_router(profiles.router)
api_router.include_router(admin.router)
