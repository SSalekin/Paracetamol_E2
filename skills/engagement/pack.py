from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from skills._utils import extract_json_object, image_payload_from_base64
from skills.common import SkillResult
from skills.engagement.judge import EngagementJudgeInput, judge_engagement


class EmotionResult(SkillResult):
    pass


class RelatabilityResult(SkillResult):
    pass


class EngagementBreakdown(BaseModel):
    emotion: EmotionResult
    relatability: RelatabilityResult
    engagement_score: int = Field(..., ge=0, le=100)
    engagement_score_raw: int = Field(..., ge=0, le=100)


SYSTEM_PROMPT = """You are a short-form engagement analyst.
Evaluate engagement potential using the provided frames, transcript, and OCR text.
Rules:
- Do not invent quotes.
- Evidence must be grounded using:
  - T: `<exact substring from transcript>`
  - O: `<exact substring from OCR text lines>`
  - V: `<visual observation from frames>`
- Use 1-3 evidence items. If you cannot ground evidence, use V: `insufficient evidence`.
Return only valid JSON with this shape:
{
  "emotion": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]},
  "relatability": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]}
}"""


async def run_engagement_pack(
    llm,
    *,
    full_transcript: str,
    hook_frames_b64: List[str],
    body_frames_b64: List[str],
    ocr_text_lines: List[str],
) -> EngagementBreakdown:
    user_content: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Transcript: {full_transcript}\n"
                f"OCR text lines: {ocr_text_lines}\n"
                "Focus on emotion triggers and relatability that drive comments/likes early."
            ),
        },
        *image_payload_from_base64((hook_frames_b64 or []) + (body_frames_b64 or [])),
    ]

    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
    )
    raw_content = getattr(response, "content", response)
    if not isinstance(raw_content, str):
        raw_content = str(raw_content)

    payload = extract_json_object(raw_content)
    emotion = EmotionResult.model_validate(payload.get("emotion"))
    relatability = RelatabilityResult.model_validate(payload.get("relatability"))
    judged = judge_engagement(EngagementJudgeInput(emotion=emotion.score, relatability=relatability.score))
    return EngagementBreakdown(
        emotion=emotion,
        relatability=relatability,
        engagement_score=judged.engagement_score,
        engagement_score_raw=judged.engagement_score_raw,
    )
