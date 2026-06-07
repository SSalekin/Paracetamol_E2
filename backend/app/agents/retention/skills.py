from backend.app.schemas.scoring import AgentSkillScore


def build_retention_skills(
    *,
    opening_pacing_score: int,
    payoff_preview_score: int,
    dropoff_risk_score: int,
    ending_drag_score: int,
    pacing_rate: float,
    reason: str,
    tips: list[str],
) -> dict[str, AgentSkillScore]:
    return {
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
    }
