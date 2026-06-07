from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from skills.hook._utils import extract_json_object, image_payload_from_base64


class VisualShockResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    evidence: List[str] = Field(default_factory=list)
    actionable_fix: str
    warnings: List[str] = Field(default_factory=list)


SYSTEM_PROMPT = """You are a visual hook specialist.
Score Visual Shock in the opening hook window using only the provided frames.
Rules:
- Evidence must be grounded using:
  - V: `<visual observation from frames>`
  - O: `<exact substring from OCR text lines>`
- Use 1-3 evidence items. If frames are unusable, use V: `insufficient evidence`.
Return only valid JSON:
{"score": 0, "confidence": 0.0, "reason": "", "evidence": [""], "actionable_fix": "", "warnings": []}"""


async def run_visual_shock_skill(
    llm,
    *,
    hook_frames_b64: List[str],
    ocr_text_lines: List[str] | None = None,
) -> VisualShockResult:
    user_content = [
        {
            "type": "text",
            "text": f"Evaluate the visual shock of the opening hook window. OCR text lines: {(ocr_text_lines or [])}",
        },
        *image_payload_from_base64(hook_frames_b64),
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
    return VisualShockResult.model_validate(payload)

