import os
import base64
from typing import List, Optional

import cv2
import numpy as np


_reader = None


def _get_reader():
    global _reader
    if _reader is not None:
        return _reader
    import easyocr

    langs = [lang.strip() for lang in (os.getenv("OCR_LANGS", "en,vi")).split(",") if lang.strip()]
    gpu = os.getenv("OCR_GPU", "").strip().lower() in {"1", "true", "yes", "on"}
    _reader = easyocr.Reader(langs, gpu=gpu)
    return _reader


def _decode_b64_jpg_to_bgr(img_b64: str) -> Optional[np.ndarray]:
    try:
        data = base64.b64decode(img_b64)
    except Exception:
        return None
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def extract_ocr_text_lines(
    hook_frames_b64: List[str],
    *,
    frame_limit: int = 5,
    min_confidence: float = 0.45,
    max_lines: int = 10,
) -> List[str]:
    try:
        reader = _get_reader()
    except Exception:
        return []

    if not hook_frames_b64:
        return []

    if frame_limit <= 0:
        frame_limit = 1

    step = max(1, round(len(hook_frames_b64) / frame_limit))
    selected = hook_frames_b64[::step][:frame_limit]

    collected: List[str] = []
    seen = set()
    max_side = int(os.getenv("OCR_IMAGE_MAX_SIDE", "0"))
    for img_b64 in selected:
        img = _decode_b64_jpg_to_bgr(img_b64)
        if img is None:
            continue

        if max_side and max_side > 0:
            h, w = img.shape[:2]
            if max(h, w) > max_side:
                scale = float(max_side) / float(max(h, w))
                new_w = max(1, int(round(w * scale)))
                new_h = max(1, int(round(h * scale)))
                img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        results = reader.readtext(img, detail=1, paragraph=False)
        for _bbox, text, conf in results:
            if conf is None or float(conf) < float(min_confidence):
                continue
            value = " ".join(str(text).split()).strip()
            if len(value) < 2:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            collected.append(value)
            if len(collected) >= max_lines:
                return collected

    return collected
