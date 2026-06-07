from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from skills._utils import extract_json_object, image_payload_from_base64
from skills.common import SkillResult
from skills.visual.judge import VisualJudgeInput, judge_visual


class ClarityResult(SkillResult):
    pass


class CompositionResult(SkillResult):
    pass


class VisualBreakdown(BaseModel):
    clarity: ClarityResult
    composition: CompositionResult
    visual_score: int = Field(..., ge=0, le=100)
    visual_score_raw: int = Field(..., ge=0, le=100)


SYSTEM_PROMPT = """You are a short-form visual quality analyst.
Evaluate visual clarity and composition using the provided frames.
Rules:
- Do not invent quotes.
- Evidence must be grounded using:
  - O: `<exact substring from OCR text lines>`
  - V: `<visual observation from frames>`
- Use 1-3 evidence items. If you cannot ground evidence, use V: `insufficient evidence`.
Return only valid JSON with this shape:
{
  "clarity": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]},
  "composition": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]}
}"""


async def run_visual_pack(
    llm,
    *,
    hook_frames_b64: List[str],
    body_frames_b64: List[str],
    ocr_text_lines: List[str],
) -> VisualBreakdown:
    user_content: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": f"OCR text lines (for readability context): {ocr_text_lines}",
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
    clarity = ClarityResult.model_validate(payload.get("clarity"))
    composition = CompositionResult.model_validate(payload.get("composition"))
    judged = judge_visual(VisualJudgeInput(clarity=clarity.score, composition=composition.score))
    return VisualBreakdown(
        clarity=clarity,
        composition=composition,
        visual_score=judged.visual_score,
        visual_score_raw=judged.visual_score_raw,
    )
