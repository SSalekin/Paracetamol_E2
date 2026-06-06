import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.core.llm import get_llm
from backend.app.schemas.scoring import AgentResult


HOOK_AGENT_SYSTEM_PROMPT = """
You are Agent 1: Hook Strength Auditor.

You evaluate only the first 3 seconds of a short-form video.

You receive:
- visual_features from OpenCV
- transcript/script text
- target niche
- target audience
- sampled first-3-second frames

Return only valid JSON matching this shape:

{
  "name": "hook_strength",
  "score": 0,
  "summary": "",
  "reason": "",
  "actionable_tips": [],
  "skills": {
    "scroll_stop": {"score": 0, "reason": "", "suggestions": []},
    "specificity": {"score": 0, "reason": "", "suggestions": []},
    "curiosity_gap": {"score": 0, "reason": "", "suggestions": []},
    "visual_disruption": {"score": 0, "reason": "", "suggestions": []}
  },
  "extra": {}
}

Rules:
- Score from 0 to 100.
- Be concrete.
- Do not say generic advice like "make it engaging".
- If evidence is missing, say that explicitly.
"""


def _image_payload(frames_b64: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_b64}",
            },
        }
        for frame_b64 in frames_b64
    ]


def _extract_json(text: str) -> dict[str, Any]:
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
        raise RuntimeError("Hook agent response did not contain JSON.")

    return json.loads(text[start : end + 1])


async def run_hook_agent(state_data: dict[str, Any]) -> AgentResult:
    llm = get_llm()

    user_text = f"""
Niche: {state_data.get("niche")}
Audience: {state_data.get("audience")}

Transcript:
{state_data.get("text_script")}

Visual features:
{state_data.get("visual_features")}

Evaluate the hook only.
"""

    user_content = [
        {"type": "text", "text": user_text},
        *_image_payload(state_data.get("hook_frames_b64", [])),
    ]

    response = await llm.ainvoke(
        [
            SystemMessage(content=HOOK_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
    )

    raw_content = getattr(response, "content", response)

    if not isinstance(raw_content, str):
        raw_content = str(raw_content)

    payload = _extract_json(raw_content)

    return AgentResult.model_validate(payload)
