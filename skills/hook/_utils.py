from typing import Any, Dict, List

from skills._utils import extract_json_object


def image_payload_from_base64(frames_b64: List[str]) -> List[Dict[str, Any]]:
    return [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
        }
        for img_b64 in frames_b64
    ]

