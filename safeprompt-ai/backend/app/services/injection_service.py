"""
Prompt injection detection service.

Milestone 6 baseline: a small, high-signal pattern matcher so the
/api/analyze endpoint returns real, working results end-to-end while the
rest of the platform (frontend, scoring, history) is built out.

Milestone 7 replaces this module entirely with the full injection
detector: a broader, curated pattern/phrase dataset covering instruction
overrides, rule resets, system-prompt extraction, security bypass,
developer-mode jailbreaks, and system-role impersonation, each with
calibrated confidence scoring and multi-match reasoning.
"""

import re
from dataclasses import dataclass


@dataclass
class InjectionDetectionResult:
    detected: bool
    confidence: float  # 0.0 - 1.0
    reason: str


# Ordered by specificity; the first match wins. Each tuple is
# (compiled pattern, confidence, human-readable reason).
_INJECTION_PATTERNS = [
    (
        re.compile(r"ignore (all |any )?(previous|prior|above|earlier) instructions", re.IGNORECASE),
        0.9,
        'Detected an instruction-override phrase ("ignore previous instructions").',
    ),
    (
        re.compile(r"forget (your|all|previous) (rules|instructions|guidelines)", re.IGNORECASE),
        0.85,
        'Detected an attempt to discard system rules ("forget your rules").',
    ),
    (
        re.compile(r"(reveal|show|print|output) (your |the )?system prompt", re.IGNORECASE),
        0.9,
        "Detected an attempt to extract the underlying system prompt.",
    ),
    (
        re.compile(r"bypass (security|safety|restrictions|filters|guardrails)", re.IGNORECASE),
        0.85,
        "Detected an explicit request to bypass safety controls.",
    ),
    (
        re.compile(r"developer mode", re.IGNORECASE),
        0.75,
        'Detected a reference to an unrestricted "developer mode" persona, a known jailbreak framing.',
    ),
    (
        re.compile(r"act as (a |the )?system", re.IGNORECASE),
        0.7,
        "Detected an attempt to impersonate the system role.",
    ),
]


def analyze_injection(prompt: str) -> InjectionDetectionResult:
    """
    Scans the prompt for known injection/jailbreak patterns and returns
    the highest-confidence match, or a clean result if none are found.
    """
    for pattern, confidence, reason in _INJECTION_PATTERNS:
        if pattern.search(prompt):
            return InjectionDetectionResult(detected=True, confidence=confidence, reason=reason)

    return InjectionDetectionResult(
        detected=False,
        confidence=0.95,
        reason="No known prompt injection patterns were found in the input.",
    )
