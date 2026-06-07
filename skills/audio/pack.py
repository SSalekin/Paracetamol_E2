from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from skills._utils import extract_json_object
from skills.common import SkillResult
from skills.audio.judge import AudioJudgeInput, judge_audio


class AudioClarityResult(SkillResult):
    pass


class AudioTrendFitResult(SkillResult):
    pass


class AudioBreakdown(BaseModel):
    audio_clarity: AudioClarityResult
    audio_trend_fit: AudioTrendFitResult
    audio_score: int = Field(..., ge=0, le=100)
    audio_score_raw: int = Field(..., ge=0, le=100)


SYSTEM_PROMPT = """You are a short-form audio analyst.
You do NOT receive raw audio. You receive transcript and optional trend context.
Evaluate:
- audio_clarity: how clear and punchy the spoken hook is (based on transcript)
- audio_trend_fit: how well audio style would fit trends (based on transcript + trend context)
Rules:
- Do not invent quotes.
- Evidence must be grounded using:
  - T: `<exact substring from transcript>`
- Use 1-3 evidence items. If transcript is missing, use T: `insufficient evidence`.
Return only valid JSON with this shape:
{
  "audio_clarity": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]},
  "audio_trend_fit": {"score":0,"confidence":0.0,"reason":"","evidence":[""],"actionable_fix":"","warnings":[]}
}"""


async def run_audio_pack(
    llm,
    *,
    transcript: str,
    trend_context: str,
) -> AudioBreakdown:
    user_content: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Transcript: {transcript}\n"
                f"Trend context: {trend_context}"
            ),
        }
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
    audio_clarity = AudioClarityResult.model_validate(payload.get("audio_clarity"))
    audio_trend_fit = AudioTrendFitResult.model_validate(payload.get("audio_trend_fit"))
    judged = judge_audio(
        AudioJudgeInput(audio_clarity=audio_clarity.score, audio_trend_fit=audio_trend_fit.score)
    )
    return AudioBreakdown(
        audio_clarity=audio_clarity,
        audio_trend_fit=audio_trend_fit,
        audio_score=judged.audio_score,
        audio_score_raw=judged.audio_score_raw,
    )
