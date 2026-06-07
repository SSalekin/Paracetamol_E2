import json
from typing import Any, Dict, List


def image_payload_from_base64(frames_b64: List[str]) -> List[Dict[str, Any]]:
    return [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
        }
        for img_b64 in frames_b64
    ]


def extract_json_object(text: str) -> Dict[str, Any]:
    raw = (text or "").strip()
    if not raw:
        raise ValueError("Model response was empty.")

    if "```" in raw:
        lines = [line for line in raw.splitlines() if not line.strip().startswith("```")]
        raw = "\n".join(lines).strip()

    decoder = json.JSONDecoder()

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    for i, ch in enumerate(raw):
        if ch not in "{[":
            continue
        try:
            parsed, _ = decoder.raw_decode(raw[i:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("Model response did not contain a valid JSON object.")
