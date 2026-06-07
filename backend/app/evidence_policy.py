import re
from typing import Any, Iterable

from pydantic import BaseModel


_BACKTICK_RE = re.compile(r"`([^`]+)`")
_QUOTE_RE = re.compile(r"\"([^\"]+)\"")


def _contains_case_insensitive(haystack: str, needle: str) -> bool:
    if not haystack or not needle:
        return False
    return needle.lower() in haystack.lower()


def _any_contains_case_insensitive(haystacks: Iterable[str], needle: str) -> bool:
    for h in haystacks:
        if _contains_case_insensitive(h, needle):
            return True
    return False


def _extract_quoted(evidence_line: str) -> str:
    line = evidence_line or ""
    m = _BACKTICK_RE.search(line)
    if m:
        return (m.group(1) or "").strip()
    m = _QUOTE_RE.search(line)
    return (m.group(1) if m else "").strip()


def _extract_grounding_substring(evidence_line: str) -> str:
    q = _extract_quoted(evidence_line)
    if q:
        return q
    line = (evidence_line or "").strip()
    if len(line) >= 2 and line[1] == ":":
        line = line[2:].strip()
    return line.strip()


def verify_evidence_and_adjust(
    obj: Any,
    *,
    transcript: str,
    ocr_text_lines: list[str],
) -> Any:
    if obj is None:
        return None

    if isinstance(obj, BaseModel):
        if hasattr(obj, "evidence") and hasattr(obj, "confidence"):
            evidence = getattr(obj, "evidence") or []
            confidence = float(getattr(obj, "confidence") or 0.0)
            warnings = list(getattr(obj, "warnings", []) or [])

            unverified = 0
            verified = 0
            for item in evidence:
                line = (item or "").strip()
                if line.startswith("T:"):
                    q = _extract_grounding_substring(line)
                    if q and _contains_case_insensitive(transcript or "", q):
                        verified += 1
                    else:
                        unverified += 1
                elif line.startswith("O:"):
                    q = _extract_grounding_substring(line)
                    if q and _any_contains_case_insensitive(ocr_text_lines or [], q):
                        verified += 1
                    else:
                        unverified += 1

            if unverified:
                warnings.append("unverified_evidence")
                confidence *= 0.7 ** unverified

            if verified == 0 and evidence:
                warnings.append("evidence_not_grounded")
                confidence *= 0.75

            if confidence < 0.0:
                confidence = 0.0
            if confidence > 1.0:
                confidence = 1.0

            setattr(obj, "confidence", confidence)
            if hasattr(obj, "warnings"):
                setattr(obj, "warnings", warnings)

        for name in obj.model_fields:
            verify_evidence_and_adjust(getattr(obj, name, None), transcript=transcript, ocr_text_lines=ocr_text_lines)
        return obj

    if isinstance(obj, list):
        for item in obj:
            verify_evidence_and_adjust(item, transcript=transcript, ocr_text_lines=ocr_text_lines)
        return obj

    if isinstance(obj, dict):
        for value in obj.values():
            verify_evidence_and_adjust(value, transcript=transcript, ocr_text_lines=ocr_text_lines)
        return obj

    return obj


def validate_evidence_strict(
    obj: Any,
    *,
    transcript: str,
    ocr_text_lines: list[str],
    allow_visual: bool,
    path: str = "",
) -> list[str]:
    errors: list[str] = []

    if obj is None:
        return errors

    if isinstance(obj, BaseModel):
        current_path = path or obj.__class__.__name__
        if hasattr(obj, "evidence") and hasattr(obj, "confidence"):
            evidence = getattr(obj, "evidence") or []
            for idx, item in enumerate(evidence):
                line = (item or "").strip()
                if not line:
                    continue
                if line.startswith("T:"):
                    q = _extract_grounding_substring(line)
                    if not q or len(q) < 3:
                        errors.append(f"{current_path}.evidence[{idx}] missing quoted substring")
                    elif not _contains_case_insensitive(transcript or "", q):
                        errors.append(f"{current_path}.evidence[{idx}] transcript substring not found: {q}")
                elif line.startswith("O:"):
                    q = _extract_grounding_substring(line)
                    if not q or len(q) < 3:
                        errors.append(f"{current_path}.evidence[{idx}] missing quoted substring")
                    elif not _any_contains_case_insensitive(ocr_text_lines or [], q):
                        errors.append(f"{current_path}.evidence[{idx}] OCR substring not found: {q}")
                elif line.startswith("V:"):
                    if not allow_visual:
                        errors.append(f"{current_path}.evidence[{idx}] visual evidence not allowed")
                else:
                    errors.append(f"{current_path}.evidence[{idx}] unknown evidence prefix")

        for name in obj.model_fields:
            next_path = f"{current_path}.{name}"
            errors.extend(
                validate_evidence_strict(
                    getattr(obj, name, None),
                    transcript=transcript,
                    ocr_text_lines=ocr_text_lines,
                    allow_visual=allow_visual,
                    path=next_path,
                )
            )
        return errors

    if isinstance(obj, list):
        for i, item in enumerate(obj):
            errors.extend(
                validate_evidence_strict(
                    item,
                    transcript=transcript,
                    ocr_text_lines=ocr_text_lines,
                    allow_visual=allow_visual,
                    path=f"{path}[{i}]",
                )
            )
        return errors

    if isinstance(obj, dict):
        for key, value in obj.items():
            errors.extend(
                validate_evidence_strict(
                    value,
                    transcript=transcript,
                    ocr_text_lines=ocr_text_lines,
                    allow_visual=allow_visual,
                    path=f"{path}.{key}" if path else str(key),
                )
            )
        return errors

    return errors
