from backend.app.agents.niche_fit.skills import build_niche_fit_skills
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

    audience_clarity_score = 75 if has_audience else 55
    niche_relevance_score = 75 if has_niche else 55
    brand_consistency_score = 65 if niche or audience else 55
    viewer_problem_score = 65 if has_niche or has_audience else 55

    return AgentResult(
        name="content_niche_fit",
        score=min(score, 90),
        summary=f"Niche fit score {min(score, 90)}/100",
        reason="Niche fit is estimated from provided niche, audience, and script alignment.",
        actionable_tips=[
            "Make the target viewer obvious in the first line, for example: 'If you are a beginner...' or 'For students who...'"
        ],
        skills=build_niche_fit_skills(
            audience_clarity_score=audience_clarity_score,
            niche_relevance_score=niche_relevance_score,
            brand_consistency_score=brand_consistency_score,
            viewer_problem_score=viewer_problem_score,
        ),
        extra={
            "niche": niche,
            "audience": audience,
            "has_niche_keyword": has_niche,
            "has_audience_keyword": has_audience,
        },
    )
