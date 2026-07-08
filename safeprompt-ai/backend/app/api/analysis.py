"""
Analysis API routes.

Exposes POST /api/analyze, which runs the injection detector, toxicity
detector, and scoring engine against a submitted prompt, persists the
result scoped to the authenticated caller, and returns the full result.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.schemas.analysis import (
    InjectionResult,
    PromptAnalysisRequest,
    PromptAnalysisResponse,
    ToxicityResult,
)
from app.schemas.auth import CurrentUser
from app.services import history_service
from app.services.injection_service import analyze_injection
from app.services.scoring_service import (
    build_reasoning,
    build_recommendation,
    calculate_safety_score,
    determine_risk_level,
)
from app.services.toxicity_service import analyze_toxicity

# No "/api" prefix here: app/api/router.py's api_router mounts this router
# directly, and main.py mounts api_router itself with prefix="/api" -- an
# extra "/api" here previously caused this to register at /api/api/analyze
# instead of /api/analyze, which the frontend (posting to /api/analyze)
# could never reach -- a plain 404, surfaced to users as axios's generic
# "Unable to reach the server" network-error message.
router = APIRouter(prefix="", tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=PromptAnalysisResponse,
    summary="Analyze a prompt for injection and toxicity risk",
    response_description="The full safety analysis result for the submitted prompt.",
)
def analyze_prompt(
    payload: PromptAnalysisRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> PromptAnalysisResponse:
    """
    Runs the injection detector and toxicity detector against the
    submitted prompt, combines their results into a safety score and
    risk level, persists the result for the authenticated user, and
    returns a full analysis with recommendation and reasoning.

    Requires authentication: results are always scoped to current_user.id,
    both in what gets persisted and in every downstream history/dashboard
    read.
    """
    try:
        injection_result = analyze_injection(payload.prompt)
        toxicity_result = analyze_toxicity(payload.prompt)
        safety_score = calculate_safety_score(injection_result, toxicity_result)
        risk_level = determine_risk_level(safety_score)
        recommendation = build_recommendation(risk_level)
        reasoning = build_reasoning(injection_result, toxicity_result)
    except Exception as exc:  # noqa: BLE001 - convert any detector failure into a clean 500
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze the prompt due to an internal error.",
        ) from exc

    result = PromptAnalysisResponse(
        prompt=payload.prompt,
        injection=InjectionResult(
            detected=injection_result.detected,
            confidence=injection_result.confidence,
            reason=injection_result.reason,
        ),
        toxicity=ToxicityResult(
            detected=toxicity_result.detected,
            category=toxicity_result.category,
            confidence=toxicity_result.confidence,
            explanation=toxicity_result.explanation,
        ),
        safety_score=safety_score,
        risk_level=risk_level,
        recommendation=recommendation,
        reasoning=reasoning,
        analyzed_at=datetime.now(timezone.utc),
    )

    # Persistence failures are logged internally and never raised — a
    # database hiccup shouldn't prevent the user from seeing their result.
    # Captures the persisted row's id and attaches it to the response --
    # previously this call's return value was discarded, so `result.id`
    # stayed None forever and every consumer that needs the id right after
    # creating an analysis (generating its report, deleting it, linking to
    # it) had no way to get one without a separate history fetch.
    created_record = history_service.create_analysis_record(current_user.id, result)
    if created_record is not None:
        result.id = created_record.get("id")

    return result
