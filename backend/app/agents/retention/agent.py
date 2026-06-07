from backend.app.agents.retention.skills import build_retention_skills
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
        skills=build_retention_skills(
            opening_pacing_score=opening_pacing_score,
            payoff_preview_score=payoff_preview_score,
            dropoff_risk_score=dropoff_risk_score,
            ending_drag_score=ending_drag_score,
            pacing_rate=pacing_rate,
            reason=reason,
            tips=tips,
        ),
        extra={
            "duration_seconds": duration,
            "pacing_rate": pacing_rate,
        },
    )
