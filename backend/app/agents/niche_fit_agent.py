from backend.app.schemas.scoring import AgentResult


async def run_niche_fit_agent(state_data: dict) -> AgentResult:
    niche = state_data.get("niche", "")
    audience = state_data.get("audience", "")
    text = state_data.get("text_script", "")

    has_niche = bool(niche and niche.lower() in text.lower())
    has_audience = bool(audience and audience.lower() in text.lower())

    score = 50

    if has_niche:
        score += 20

    if has_audience:
        score += 10

    return AgentResult(
        name="content_niche_fit",
        score=min(score, 90),
        summary=f"Niche fit score {min(score, 90)}/100",
        reason="Niche fit is estimated from provided niche, audience, and script alignment.",
        actionable_tips=[
            "Make the target viewer obvious in the first line, for example: 'If you are a beginner...' or 'For students who...'"
        ],
        skills={},
        extra={
            "niche": niche,
            "audience": audience,
            "has_niche_keyword": has_niche,
            "has_audience_keyword": has_audience,
        },
    )
