"""
Unit tests for the Milestone 9 Safety Score Engine
(app/services/scoring_engine.py), in isolation from the detectors and API
layer. Constructs InjectionDetectionResult/ToxicityDetectionResult
directly so each test exercises one property of the scoring model without
depending on regex/keyword fallback behavior.
"""

from app.services.detectors.injection_detector import InjectionDetectionResult
from app.services.detectors.toxicity_detector import ToxicityDetectionResult
from app.services.scoring_engine import compute_score


def _injection(detected=False, penalty=0, confidence=0.0, method="regex", reasons=None):
    return InjectionDetectionResult(
        detected=detected,
        penalty=penalty,
        confidence=confidence,
        method=method,
        reasons=reasons or [],
    )


def _toxicity(detected=False, penalty=0, scores=None, method="keyword", reasons=None):
    return ToxicityDetectionResult(
        detected=detected,
        penalty=penalty,
        scores=scores or {},
        method=method,
        reasons=reasons or [],
    )


def test_no_signals_scores_perfect_and_safe():
    breakdown = compute_score(_injection(), _toxicity())
    assert breakdown.score == 100.0
    assert breakdown.risk_level == "safe"
    assert breakdown.injection_risk == 0.0
    assert breakdown.toxicity_risk == 0.0
    assert breakdown.floor_applied is False


def test_high_confidence_regex_injection_triggers_floor():
    # A regex match always has confidence == 1.0, which is above the
    # default 0.9 floor threshold, so the score should be hard-capped.
    breakdown = compute_score(
        _injection(detected=True, penalty=45, confidence=1.0), _toxicity()
    )
    assert breakdown.floor_applied is True
    assert breakdown.score <= 15.0
    assert breakdown.risk_level == "critical"


def test_low_confidence_signals_do_not_trigger_floor():
    breakdown = compute_score(
        _injection(detected=True, penalty=20, confidence=0.3), _toxicity()
    )
    assert breakdown.floor_applied is False


def test_combined_risk_is_worse_than_either_signal_alone():
    injection_only = compute_score(
        _injection(detected=True, penalty=20, confidence=0.4), _toxicity()
    )
    toxicity_only = compute_score(
        _injection(), _toxicity(detected=True, penalty=20, scores={"toxicity": 0.4})
    )
    both = compute_score(
        _injection(detected=True, penalty=20, confidence=0.4),
        _toxicity(detected=True, penalty=20, scores={"toxicity": 0.4}),
    )
    assert both.score < injection_only.score
    assert both.score < toxicity_only.score
    assert both.combined_risk > injection_only.combined_risk
    assert both.combined_risk > toxicity_only.combined_risk


def test_toxicity_severity_falls_back_to_penalty_when_no_scores():
    # Keyword fallback mode never populates `scores`, so severity should
    # be approximated from the penalty instead of always reading as 0.
    with_scores = compute_score(
        _injection(), _toxicity(detected=True, penalty=40, scores={"toxicity": 0.9})
    )
    without_scores = compute_score(
        _injection(), _toxicity(detected=True, penalty=40, scores={})
    )
    assert without_scores.toxicity_risk > 0
    # Real per-category severity (0.9) should weigh in as riskier than
    # the penalty-only proxy for the same 40-point penalty.
    assert with_scores.toxicity_risk > without_scores.toxicity_risk


def test_score_and_risk_level_are_monotonic_with_penalty():
    low = compute_score(_injection(detected=True, penalty=10, confidence=0.2), _toxicity())
    high = compute_score(_injection(detected=True, penalty=80, confidence=0.2), _toxicity())
    assert high.score < low.score


def test_score_never_goes_out_of_bounds():
    breakdown = compute_score(
        _injection(detected=True, penalty=100, confidence=1.0),
        _toxicity(detected=True, penalty=100, scores={"toxicity": 1.0, "threat": 1.0}),
    )
    assert 0.0 <= breakdown.score <= 100.0
