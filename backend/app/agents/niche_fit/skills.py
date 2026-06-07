from backend.app.schemas.scoring import AgentSkillScore


def build_niche_fit_skills(
    *,
    audience_clarity_score: int,
    niche_relevance_score: int,
    brand_consistency_score: int,
    viewer_problem_score: int,
) -> dict[str, AgentSkillScore]:
    return {
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
    }
