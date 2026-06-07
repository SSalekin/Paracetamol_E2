from backend.app.agents.trend.skills import (
    build_missing_trend_skills,
    build_supplied_trend_skills,
)
from backend.app.schemas.scoring import AgentResult


async def run_trend_agent(state_data: dict) -> AgentResult:
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
