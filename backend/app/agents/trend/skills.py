from backend.app.schemas.scoring import AgentSkillScore


def build_missing_trend_skills() -> dict[str, AgentSkillScore]:
    return {
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
    }


def build_supplied_trend_skills() -> dict[str, AgentSkillScore]:
    return {
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
    }
