from backend.app.schemas.scoring import AgentResult, AgentSkillScore


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
            skills={
                "trend_context_available": AgentSkillScore(
                    score=35,
                    reason="No sound, trend age, or keyword trend context was provided.",
                    suggestions=["Provide the sound name, trend age, or current keyword trend data."],
                ),
                "sound_freshness": AgentSkillScore(
                    score=50,
                    reason="Sound freshness cannot be verified without trend context.",
                    suggestions=["Add whether the audio is emerging, peaking, or declining."],
                ),
                "audio_visual_sync": AgentSkillScore(
                    score=55,
                    reason="Audio/video beat sync is not available from the current extracted visual-only data.",
                    suggestions=["Align the first visual cut or gesture with the sound's first beat."],
                ),
                "trend_fit": AgentSkillScore(
                    score=55,
                    reason="Trend fit cannot be confirmed without the sound or keyword context.",
                    suggestions=["Explain why this trend matches the niche and audience."],
                ),
            },
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
        skills={
            "trend_context_available": AgentSkillScore(
                score=80,
                reason="Trend context was supplied.",
                suggestions=["Keep trend metadata attached to future scoring requests."],
            ),
            "sound_freshness": AgentSkillScore(
                score=65,
                reason="Freshness is estimated from supplied context; no live trend API verification is implemented yet.",
                suggestions=["Replace manual context with live trend age/freshness data."],
            ),
            "audio_visual_sync": AgentSkillScore(
                score=60,
                reason="Audio/video sync cannot be measured from text-only trend context.",
                suggestions=["Cut or gesture on the sound's first beat."],
            ),
            "trend_fit": AgentSkillScore(
                score=70,
                reason="Trend context was supplied, so fit can be considered by the final scorer.",
                suggestions=["Make the trend serve the niche rather than using it as background audio only."],
            ),
        },
        extra={
            "trend_context_available": True,
            "trend_context": trend_context,
            "heuristic_only": True,
            "confidence": "medium",
        },
    )
