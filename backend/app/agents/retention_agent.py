from backend.app.schemas.scoring import AgentResult


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

    return AgentResult(
        name="completion_rate",
        score=score,
        summary=f"Retention score {score}/100",
        reason=reason,
        actionable_tips=tips,
        skills={},
        extra={
            "duration_seconds": duration,
            "pacing_rate": pacing_rate,
        },
    )
