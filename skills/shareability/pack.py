from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from skills._utils import extract_json_object, image_payload_from_base64
from skills.common import SkillResult
from skills.shareability.judge import ShareabilityJudgeInput, judge_shareability


class ValueDensityResult(SkillResult):
    pass


class SaveShareCtaResult(SkillResult):
    pass


class ShareabilityBreakdown(BaseModel):
    value_density: ValueDensityResult
    save_share_cta: SaveShareCtaResult
    shareability_score: int = Field(..., ge=0, le=100)
    shareability_score_raw: int = Field(..., ge=0, le=100)


SYSTEM_PROMPT = """You are a short-form shareability analyst.
Evaluate save/share potential using frames, transcript, and OCR text.
Rules:
- Do not invent quotes.
- Evidence must be grounded using:
  - T: `<exact substring from transcript>`
  - O: `<exact substring from OCR text lines>`
  - V: `<visual observation from frames>`
- Use 1-3 evidence items. If you cannot ground evidence, use V: `insufficient evidence`.
Return only valid JSON with this shape:
{
  "value_density": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]},
  "save_share_cta": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]}
}"""


async def run_shareability_pack(
    llm,
    *,
    full_transcript: str,
    hook_frames_b64: List[str],
    body_frames_b64: List[str],
    ocr_text_lines: List[str],
) -> ShareabilityBreakdown:
    user_content: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Transcript: {full_transcript}\n"
                f"OCR text lines: {ocr_text_lines}\n"
                "Focus on value density and whether a strong save/share CTA exists."
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
    value_density = ValueDensityResult.model_validate(payload.get("value_density"))
    save_share_cta = SaveShareCtaResult.model_validate(payload.get("save_share_cta"))
    judged = judge_shareability(
        ShareabilityJudgeInput(value_density=value_density.score, save_share_cta=save_share_cta.score)
    )
    return ShareabilityBreakdown(
        value_density=value_density,
        save_share_cta=save_share_cta,
        shareability_score=judged.shareability_score,
        shareability_score_raw=judged.shareability_score_raw,
    )
