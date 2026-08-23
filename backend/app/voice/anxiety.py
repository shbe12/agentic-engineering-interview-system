"""Lightweight rule-based empathy/anxiety heuristic on the candidate's voice answer, per
spec: "if the voice is too fast or stuttering, then it means the student might be anxious."
This is intentionally a simple MVP heuristic (speaking rate + disfluency markers), not a
trained classifier — easy to swap for a real model later without touching callers.
"""

import re

FAST_WPM_THRESHOLD = 170
DISFLUENCY_THRESHOLD = 3

_FILLER_RE = re.compile(r"\b(um+|uh+|erm+|like)\b", re.IGNORECASE)
_REPEATED_WORD_RE = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)


def detect_anxiety(text: str, duration_seconds: float, word_count: int) -> dict:
    wpm = (word_count / duration_seconds * 60) if duration_seconds > 0 else 0.0
    disfluency_count = len(_FILLER_RE.findall(text)) + len(_REPEATED_WORD_RE.findall(text))

    reasons = []
    if wpm > FAST_WPM_THRESHOLD:
        reasons.append(f"fast speech ({wpm:.0f} wpm)")
    if disfluency_count >= DISFLUENCY_THRESHOLD:
        reasons.append(f"stuttering/filler words (x{disfluency_count})")

    return {
        "anxious": bool(reasons),
        "reason": ", ".join(reasons) if reasons else "",
        "wpm": wpm,
        "disfluency_count": disfluency_count,
    }
