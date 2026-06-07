from typing import Any

from pydantic import BaseModel

from backend.app.confidence_policy import apply_confidence_policy


def adjust_confidence(obj: Any, *, quality_flags: list[str]) -> Any:
    if obj is None:
        return None

    if isinstance(obj, BaseModel):
        if hasattr(obj, "confidence"):
            value = getattr(obj, "confidence")
            setattr(obj, "confidence", apply_confidence_policy(float(value or 0.0), quality_flags=quality_flags))

        for name in obj.model_fields:
            adjust_confidence(getattr(obj, name, None), quality_flags=quality_flags)
        return obj

    if isinstance(obj, list):
        for item in obj:
            adjust_confidence(item, quality_flags=quality_flags)
        return obj

    if isinstance(obj, dict):
        for value in obj.values():
            adjust_confidence(value, quality_flags=quality_flags)
        return obj

    return obj

