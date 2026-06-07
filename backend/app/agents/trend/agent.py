from backend.app.agents.trend.skills import (
    build_missing_trend_skills,
    build_supplied_trend_skills,
)
from backend.app.agents.common import run_intelligent_agent
from backend.app.schemas.scoring import AgentResult


TREND_SYSTEM_PROMPT = """You are the Sound Trend Timing Agent.
Judge whether the sound/trend context supports distribution. Consider trend context availability, sound freshness, audio-visual sync opportunity, and trend fit for the niche.

Return only valid JSON matching this shape:
{
  "name": "sound_trend_timing",
  "score": 0,
  "summary": "",
  "reason": "",
  "actionable_tips": [],
  "skills": {
    "trend_context_available": {"score": 0, "reason": "", "suggestions": []},
    "sound_freshness": {"score": 0, "reason": "", "suggestions": []},
    "audio_visual_sync": {"score": 0, "reason": "", "suggestions": []},
    "trend_fit": {"score": 0, "reason": "", "suggestions": []}
  },
  "extra": {}
}

If trend context is missing, score uncertainty neutrally and specify what data is needed."""


def build_trend_fallback(state_data: dict) -> AgentResult:
    trend_context = state_data.get("trend_context", "")

    missing = (
        not trend_context
        or "not provided" in trend_context.lower()
    )

    if missing:
        return AgentResult(
            name="sound_trend_timing",
            score=60,
            summary="Trend timing unknown",
            reason="No live audio or trend context was provided, so trend timing cannot be verified. This is neutral uncertainty, not evidence that the video is weak.",
            actionable_tips=[
                "Provide the sound name, trend age, or keyword trend context before scoring this dimension."
            ],
            skills=build_missing_trend_skills(),
            extra={
                "trend_context_available": False,
                "heuristic_only": True,
                "confidence": "low",
            },
        )

    return AgentResult(
        name="sound_trend_timing",
        score=70,
        summary="Trend context provided",
        reason="Trend context was supplied, but no real trend API verification is implemented yet.",
        actionable_tips=[
            "Replace this placeholder with a real trend API or manually supplied trend freshness score."
        ],
        skills=build_supplied_trend_skills(),
        extra={
            "trend_context_available": True,
            "trend_context": trend_context,
            "heuristic_only": True,
            "confidence": "medium",
        },
    )


async def run_trend_agent(state_data: dict) -> AgentResult:
    return await run_intelligent_agent(
        agent_name="trend_agent",
        system_prompt=TREND_SYSTEM_PROMPT,
        state_data=state_data,
        fallback_result=build_trend_fallback(state_data),
        focus="Evaluate sound trend timing, sound freshness, audio-visual sync, and trend fit.",
    )
