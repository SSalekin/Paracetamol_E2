import base64
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import cv2
import numpy as np


@dataclass
class VideoSignals:
    video_path: str
    transcript: str
    transcript_source: str
    trend_context: str
    hook_frames_b64: List[str]
    body_frames_b64: List[str]
    ocr_text_lines: List[str]
    quality_flags: List[str]
    quality_metrics: Dict[str, Any]

    def fingerprint_payload(self) -> Dict[str, Any]:
        return {
            "transcript": (self.transcript or "")[:500],
            "trend_context": (self.trend_context or "")[:500],
            "hook_frames_count": len(self.hook_frames_b64 or []),
            "body_frames_count": len(self.body_frames_b64 or []),
            "ocr_lines": self.ocr_text_lines or [],
            "quality_flags": self.quality_flags or [],
        }


def _decode_b64_jpg(img_b64: str) -> Optional[np.ndarray]:
    try:
        data = base64.b64decode(img_b64)
    except Exception:
        return None
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def _frame_brightness(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def assess_frame_quality(frames_b64: List[str]) -> Dict[str, Any]:
    values: List[float] = []
    for b64 in (frames_b64 or [])[:10]:
        img = _decode_b64_jpg(b64)
        if img is None:
            continue
        values.append(_frame_brightness(img))

    if not values:
        return {"avg_brightness": None, "dark_ratio": None, "sampled": 0}

    avg = float(sum(values) / len(values))
    dark = sum(1 for v in values if v < 18.0)
    return {"avg_brightness": avg, "dark_ratio": float(dark) / len(values), "sampled": len(values)}


def build_quality_flags(
    *,
    transcript: str,
    transcript_source: str,
    hook_frames_b64: List[str],
    body_frames_b64: List[str],
    ocr_text_lines: List[str],
) -> tuple[List[str], Dict[str, Any]]:
    flags: List[str] = []
    metrics: Dict[str, Any] = {
        "hook_frames": len(hook_frames_b64 or []),
        "body_frames": len(body_frames_b64 or []),
        "ocr_lines": len(ocr_text_lines or []),
        "transcript_source": transcript_source,
        "transcript_len": len((transcript or "").strip()),
    }

    if not hook_frames_b64:
        flags.append("missing_hook_frames")
    if (transcript or "").strip() in ("", "Transcript was not provided."):
        flags.append("missing_transcript")
    if transcript_source == "whisper" and len((transcript or "").strip()) < 10:
        flags.append("weak_transcript")

    frame_metrics = assess_frame_quality(hook_frames_b64 or [])
    metrics["hook_frame_quality"] = frame_metrics
    if frame_metrics.get("dark_ratio") is not None and float(frame_metrics["dark_ratio"]) >= 0.6:
        flags.append("hook_frames_too_dark")

    if not (ocr_text_lines or []):
        flags.append("no_ocr_text")

    return flags, metrics

