"""
Prompt analysis service — orchestration layer.

Milestone 6 introduced this module as a self-contained interim heuristic.
Milestones 7 and 8 moved the actual detection logic out into dedicated
modules:

  - app/services/detectors/injection_detector.py (Milestone 7)
  - app/services/detectors/toxicity_detector.py  (Milestone 8)

Milestone 9 moved score/risk-level calculation out into
app/services/scoring_engine.py — a confidence-aware, non-linear model
that replaces the original flat `100 - penalties` subtraction (see that
module's docstring for the full rationale). This module now just calls
both detectors, hands their output to `compute_score()`, and builds the
AnalyzeResponse. Milestone 10 (SQLite database) adds persistence of each
analysis, wired up at the API route layer (app/api/routes/analysis.py)
rather than here, so `analyze_prompt()` stays a pure function with no
database dependency.
"""

from app.schemas.analysis import AnalyzeResponse
from app.services.detectors.injection_detector import detect_injection
from app.services.detectors.toxicity_detector import detect_toxicity
from app.services.scoring_engine import compute_score


def _recommendation_for(risk_level: str, injection: bool, toxicity: bool) -> str:
    if risk_level == "safe":
        return "No action needed. This prompt appears safe to process."
    if risk_level == "low":
        return "Likely safe. Review is optional but not required."
    if injection and toxicity:
        return "Block this prompt. It shows signs of both instruction override and toxic language."
    if injection:
        return "Block this prompt. It attempts to override system instructions."
    if toxicity:
        return "Flag this prompt for review due to hostile or toxic language."
    return "Review recommended before processing this prompt."


def analyze_prompt(prompt: str) -> AnalyzeResponse:
    """
    Runs the Milestone 7 injection detector and Milestone 8 toxicity
    detector over the given text, combines their output via the
    Milestone 9 Safety Score Engine, and returns a full AnalyzeResponse
    with a 0-100 safety score, risk level, recommendation, and
    human-readable reasoning. Pure function — no persistence; the API
    route layer is responsible for saving the result (Milestone 10).
    """
    injection = detect_injection(prompt)
    toxicity = detect_toxicity(prompt)

    breakdown = compute_score(injection, toxicity)

    reasoning = [*injection.reasons, *toxicity.reasons]
    if not reasoning:
        reasoning.append("No injection patterns or toxic language detected.")
    if breakdown.floor_applied:
        reasoning.append(
            "Score capped due to a single high-confidence detection signal, "
            "overriding the blended risk calculation."
        )

    return AnalyzeResponse(
        prompt=prompt,
        score=breakdown.score,
        risk_level=breakdown.risk_level,
        injection_detected=injection.detected,
        toxicity_detected=toxicity.detected,
        injection_confidence=injection.confidence,
        toxicity_scores=toxicity.scores,
        recommendation=_recommendation_for(
            breakdown.risk_level, injection.detected, toxicity.detected
        ),
        reasoning=reasoning,
    )
