from __future__ import annotations

from .models import ModerationResult


BLOCKED_TERMS = {
    "exploit instructions",
    "malware",
    "violent threat",
}


def moderate_text(text: str) -> ModerationResult:
    lowered = text.lower()
    for term in BLOCKED_TERMS:
        if term in lowered:
            return ModerationResult(
                allowed=False,
                reason=f"Content blocked by policy term: {term}",
            )
    return ModerationResult(allowed=True)
