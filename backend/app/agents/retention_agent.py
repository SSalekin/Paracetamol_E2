from backend.app.schemas.scoring import AgentResult, AgentSkillScore


async def run_retention_agent(state_data: dict) -> AgentResult:
    visual_features = state_data.get("visual_features", {})
    duration = visual_features.get("duration_seconds", 0)
    pacing_rate = visual_features.get("pacing_rate", 0)

    if duration <= 4:
        score = 70
        reason = "The video is very short, so completion risk is lower, but retention cannot be fully inferred from hook frames only."
        tips = ["Avoid adding an outro; end immediately after the main payoff."]
    elif pacing_rate < 0.5:
        score = 45
        reason = "Low pacing in the opening may cause early drop-off."
        tips = ["Add a visual cut, zoom, or overlay change within the first second."]
    else:
        score = 65
        reason = "Opening pacing is acceptable, but full-body retention evidence is limited."
        tips = ["Add a payoff preview before second 2."]

    opening_pacing_score = 45 if pacing_rate < 0.5 and duration > 4 else min(85, 60 + int(pacing_rate * 12))
    payoff_preview_score = 55 if duration > 4 else 70
    dropoff_risk_score = score
    ending_drag_score = 70 if duration <= 4 else 60

    return AgentResult(
        name="completion_rate",
        score=score,
        summary=f"Retention score {score}/100",
        reason=reason,
        actionable_tips=tips,
        skills={
            "opening_pacing": AgentSkillScore(
                score=opening_pacing_score,
                reason=f"Estimated from opening pacing rate {pacing_rate}.",
                suggestions=["Add a visible cut, zoom, or overlay change inside the first second."],
            ),
            "payoff_preview": AgentSkillScore(
                score=payoff_preview_score,
                reason="Estimated from whether the short opening gives enough evidence of an early payoff.",
                suggestions=["Preview the payoff before second 2 so viewers know why to stay."],
            ),
            "dropoff_risk": AgentSkillScore(
                score=dropoff_risk_score,
                reason=reason,
                suggestions=tips,
            ),
            "ending_drag": AgentSkillScore(
                score=ending_drag_score,
                reason="Short videos have less room for outro drag; longer videos need stronger ending discipline.",
                suggestions=["Cut the video immediately after the payoff; avoid verbal outro cues."],
            ),
        },
        extra={
            "duration_seconds": duration,
            "pacing_rate": pacing_rate,
        },
    )
