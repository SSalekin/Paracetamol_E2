from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from skills._utils import extract_json_object, image_payload_from_base64
from skills.common import SkillResult
from skills.trend.judge import TrendJudgeInput, judge_trend


class TrendTopicResult(SkillResult):
    pass


class TrendFormatResult(SkillResult):
    pass


class TrendBreakdown(BaseModel):
    trend_topic: TrendTopicResult
    trend_format: TrendFormatResult
    trend_score: int = Field(..., ge=0, le=100)
    trend_score_raw: int = Field(..., ge=0, le=100)


SYSTEM_PROMPT = """You are a short-form trend analyst.
Evaluate trend alignment using the provided frames, transcript, OCR text, and optional trend context.
Rules:
- Do not invent quotes.
- Evidence must be grounded using:
  - T: `<exact substring from transcript>`
  - O: `<exact substring from OCR text lines>`
  - V: `<visual observation from frames>`
- Use 1-3 evidence items. If you cannot ground evidence, use V: `insufficient evidence`.
Return only valid JSON with this shape:
{
  "trend_topic": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]},
  "trend_format": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]}
}"""


async def run_trend_pack(
    llm,
    *,
    full_transcript: str,
    hook_frames_b64: List[str],
    body_frames_b64: List[str],
    ocr_text_lines: List[str],
    trend_context: str,
) -> TrendBreakdown:
    user_content: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Transcript: {full_transcript}\n"
                f"OCR text lines: {ocr_text_lines}\n"
                f"Trend context: {trend_context}\n"
                "Focus on topic relevance and format fit (style, structure, pacing) for current trends."
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
    trend_topic = TrendTopicResult.model_validate(payload.get("trend_topic"))
    trend_format = TrendFormatResult.model_validate(payload.get("trend_format"))
    judged = judge_trend(TrendJudgeInput(trend_topic=trend_topic.score, trend_format=trend_format.score))
    return TrendBreakdown(
        trend_topic=trend_topic,
        trend_format=trend_format,
        trend_score=judged.trend_score,
        trend_score_raw=judged.trend_score_raw,
    )
