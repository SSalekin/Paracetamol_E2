from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from skills._utils import extract_json_object, image_payload_from_base64
from skills.common import SkillResult
from skills.retention.judge import RetentionJudgeInput, judge_retention


class PacingResult(SkillResult):
    pass


class AttentionDecayResult(SkillResult):
    pass


class RetentionBreakdown(BaseModel):
    pacing: PacingResult
    attention_decay: AttentionDecayResult
    retention_score: int = Field(..., ge=0, le=100)
    retention_score_raw: int = Field(..., ge=0, le=100)


SYSTEM_PROMPT = """You are a short-form retention analyst.
Evaluate retention potential using the provided frames, transcript, and OCR text.
Rules:
- Do not invent quotes.
- Evidence must be grounded using:
  - T: `<exact substring from transcript>`
  - O: `<exact substring from OCR text lines>`
  - V: `<visual observation from frames>`
- Use 1-3 evidence items. If you cannot ground evidence, use V: `insufficient evidence`.
Return only valid JSON with this shape:
{
  "pacing": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]},
  "attention_decay": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]}
}"""


async def run_retention_pack(
    llm,
    *,
    full_transcript: str,
    hook_frames_b64: List[str],
    body_frames_b64: List[str],
    ocr_text_lines: List[str],
) -> RetentionBreakdown:
    user_content: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Transcript: {full_transcript}\n"
                f"OCR text lines: {ocr_text_lines}\n"
                "Focus on pacing (cuts, scene changes, dead time) and attention decay (predict where viewers drop)."
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
    pacing = PacingResult.model_validate(payload.get("pacing"))
    attention_decay = AttentionDecayResult.model_validate(payload.get("attention_decay"))
    judged = judge_retention(RetentionJudgeInput(pacing=pacing.score, attention_decay=attention_decay.score))
    return RetentionBreakdown(
        pacing=pacing,
        attention_decay=attention_decay,
        retention_score=judged.retention_score,
        retention_score_raw=judged.retention_score_raw,
    )
