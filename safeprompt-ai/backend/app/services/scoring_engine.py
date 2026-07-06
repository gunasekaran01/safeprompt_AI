"""
Safety Score Engine — Milestone 9.

Milestones 6-8 combined detector output with a flat additive subtraction:

    score = 100 - injection.penalty - toxicity.penalty

That works, but it has two weaknesses this module fixes:

1. It only looks at each detector's `penalty`, ignoring `confidence`
   (injection) and per-category `scores` (toxicity) — two prompts with the
   same penalty but very different confidence get the same score.
2. Flat subtraction double-penalizes prompts flagged by both detectors
   (the two penalties simply stack, with no cap on how they interact) and
   under-penalizes a single very-high-confidence signal if its raw
   penalty happens to be moderate.

This module instead:

1. Blends each detector's penalty *and* confidence/severity into a single
   0-1 "risk" score for that detector (`_injection_risk`,
   `_toxicity_risk`), weighted via `Settings.SCORE_*_WEIGHT`.
2. Combines the two per-detector risks with a probabilistic OR
   (`1 - (1 - a) * (1 - b)`) rather than flat addition, so two
   simultaneous moderate signals compound smoothly without needing an
   arbitrary min/max cap.
3. Applies a hard safety floor: if either detector's confidence/severity
   alone crosses `Settings.SCORE_HIGH_CONFIDENCE_FLOOR_THRESHOLD`, the
   score is capped at `Settings.SCORE_HIGH_CONFIDENCE_SCORE_CAP` even if
   the blended calculation would have produced something higher — a
   confirmed attack shouldn't be diluted just because the prompt wasn't
   *also* toxic (or vice versa).

`analyze_prompt()` in analysis_service.py calls `compute_score()` and
uses the returned `ScoreBreakdown.score`/`risk_level` to build the
AnalyzeResponse. The AnalyzeResponse contract itself does not change.
"""

from dataclasses import dataclass

from app.core.config import get_settings
from app.services.detectors.injection_detector import InjectionDetectionResult
from app.services.detectors.toxicity_detector import ToxicityDetectionResult

settings = get_settings()


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass
class ScoreBreakdown:
    """
    Result of combining detector output into a final safety score.

    Exposes the intermediate per-detector risk values (not just the final
    score) so callers — and tests — can reason about *why* a score came
    out the way it did, not just what it is.
    """

    score: float
    risk_level: str
    injection_risk: float
    toxicity_risk: float
    combined_risk: float
    floor_applied: bool


def _risk_level_from_score(score: float) -> str:
    """
    Classifies a 0-100 score into safe/low/medium/high/critical using the
    thresholds in app/core/config.py — the single source of truth also
    mirrored on the frontend in utils/riskLevels.js.
    """
    if score >= settings.RISK_THRESHOLD_SAFE:
        return "safe"
    if score >= settings.RISK_THRESHOLD_LOW:
        return "low"
    if score >= settings.RISK_THRESHOLD_MEDIUM:
        return "medium"
    if score >= settings.RISK_THRESHOLD_HIGH:
        return "high"
    return "critical"


def _injection_risk(result: InjectionDetectionResult) -> float:
    """Blends injection penalty and confidence into a single 0-1 risk."""
    penalty_component = _clamp(result.penalty / 100)
    confidence_component = _clamp(result.confidence)
    return _clamp(
        settings.SCORE_INJECTION_PENALTY_WEIGHT * penalty_component
        + settings.SCORE_INJECTION_CONFIDENCE_WEIGHT * confidence_component
    )


def _toxicity_severity(result: ToxicityDetectionResult) -> float:
    """
    The strongest single per-category Detoxify score (0-1), used as the
    "how bad is the worst category" severity signal. The keyword fallback
    has no per-category scores, so its penalty (already 0-100) is used as
    a proxy instead.
    """
    if result.scores:
        return _clamp(max(result.scores.values()))
    return _clamp(result.penalty / 100)


def _toxicity_risk(result: ToxicityDetectionResult) -> float:
    """Blends toxicity penalty and severity into a single 0-1 risk."""
    penalty_component = _clamp(result.penalty / 100)
    severity_component = _toxicity_severity(result)
    return _clamp(
        settings.SCORE_TOXICITY_PENALTY_WEIGHT * penalty_component
        + settings.SCORE_TOXICITY_SEVERITY_WEIGHT * severity_component
    )


def compute_score(
    injection: InjectionDetectionResult, toxicity: ToxicityDetectionResult
) -> ScoreBreakdown:
    """
    Combines the Milestone 7 injection detector and Milestone 8 toxicity
    detector outputs into a single 0-100 safety score and risk level.
    """
    injection_risk = _injection_risk(injection)
    toxicity_risk = _toxicity_risk(toxicity)

    # Probabilistic OR: treat each per-detector risk as the probability
    # the prompt is unsafe from that angle, and combine them so two
    # simultaneous moderate signals compound instead of being flatly
    # summed (which can over-penalize) or maxed (which ignores the
    # weaker signal entirely).
    combined_risk = 1 - (1 - injection_risk) * (1 - toxicity_risk)
    score = 100 * (1 - combined_risk)

    # Hard safety floor for a single very-high-confidence/severity signal.
    floor_applied = False
    strongest_signal = max(injection.confidence, _toxicity_severity(toxicity))
    if strongest_signal >= settings.SCORE_HIGH_CONFIDENCE_FLOOR_THRESHOLD:
        capped_score = min(score, settings.SCORE_HIGH_CONFIDENCE_SCORE_CAP)
        floor_applied = capped_score < score
        score = capped_score

    score = round(_clamp(score, 0, 100), 2)
    risk_level = _risk_level_from_score(score)

    return ScoreBreakdown(
        score=score,
        risk_level=risk_level,
        injection_risk=round(injection_risk, 4),
        toxicity_risk=round(toxicity_risk, 4),
        combined_risk=round(combined_risk, 4),
        floor_applied=floor_applied,
    )
