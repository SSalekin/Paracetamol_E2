from backend.app.schemas.scoring import AgentResult, AgentSkillScore


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
        skills={
            "audience_clarity": AgentSkillScore(
                score=audience_clarity_score,
                reason="Estimated from whether the supplied audience appears in the script.",
                suggestions=["Name the target viewer or situation in the first line."],
            ),
            "niche_relevance": AgentSkillScore(
                score=niche_relevance_score,
                reason="Estimated from whether the supplied niche appears in the script.",
                suggestions=["Make the niche category explicit in speech or on-screen text."],
            ),
            "brand_consistency": AgentSkillScore(
                score=brand_consistency_score,
                reason="Estimated from available niche and audience metadata.",
                suggestions=["Use visuals, words, and payoff that all point to the same niche promise."],
            ),
            "viewer_problem_match": AgentSkillScore(
                score=viewer_problem_score,
                reason="Estimated from whether the script connects to the target viewer or niche problem.",
                suggestions=["State the viewer problem before showing the solution or payoff."],
            ),
        },
        extra={
            "niche": niche,
            "audience": audience,
            "has_niche_keyword": has_niche,
            "has_audience_keyword": has_audience,
        },
    )
