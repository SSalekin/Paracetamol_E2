import json
from typing import Any


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    if "```" in text:
        lines = [
            line
            for line in text.splitlines()
            if not line.strip().startswith("```")
        ]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Final scorer response did not contain JSON.")

    return json.loads(text[start : end + 1])


def image_payload(frames_b64: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_b64}",
            },
        }
        for frame_b64 in frames_b64
    ]


def build_user_text(state_data: dict[str, Any]) -> str:
    return f"""--- METADATA ---
Target Niche: {state_data.get("niche")}
Target Audience: {state_data.get("audience")}
Planned Posting Time: {state_data.get("posting_time")}

--- TRANSCRIPT / SCRIPT ---
{state_data.get("text_script")}

--- LIVE TREND / KEYWORD CONTEXT ---
{state_data.get("trend_context")}

--- ACTUAL VIDEO CONTEXT ---
{state_data.get("actual_video_context")}

--- OPENCV VISUAL FEATURES ---
{state_data.get("visual_features")}

--- SPECIALIST AGENT FINDINGS ---
{json.dumps(state_data.get("agent_results", {}), ensure_ascii=False, indent=2)}

Important: the specialist findings above are advisory. If an agent says "heuristic_only" or "confidence: low", treat its numeric score as weak evidence. Do not average the specialist scores mechanically.

Produce a monolith-quality final report with specific explanations, concrete fixes, realistic retention drop zones, and a script variant that addresses the biggest weakness."""
