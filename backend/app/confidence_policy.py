from typing import Tuple


def apply_confidence_policy(confidence: float, *, quality_flags: list[str]) -> float:
    value = float(confidence or 0.0)
    if value < 0.0:
        value = 0.0
    if value > 1.0:
        value = 1.0

    penalties = {
        "missing_transcript": 0.65,
        "weak_transcript": 0.80,
        "missing_hook_frames": 0.40,
        "hook_frames_too_dark": 0.70,
        "no_ocr_text": 0.85,
    }

    for flag in quality_flags or []:
        factor = penalties.get(flag)
        if factor is not None:
            value *= float(factor)

    if value < 0.0:
        value = 0.0
    if value > 1.0:
        value = 1.0
    return value


def blend_score(base_score: int, skill_score: int, *, base_weight: float = 0.6) -> int:
    b = int(base_score or 0)
    s = int(skill_score or 0)
    w = float(base_weight)
    if w < 0.0:
        w = 0.0
    if w > 1.0:
        w = 1.0
    value = round(w * b + (1.0 - w) * s)
    if value < 0:
        value = 0
    if value > 100:
        value = 100
    return value

