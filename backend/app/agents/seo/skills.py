from backend.app.schemas.scoring import AgentSkillScore


def build_seo_skills(
    *,
    spoken_keyword_score: int,
    on_screen_keyword_score: int,
    niche_query_match_score: int,
    search_intent_clarity_score: int,
) -> dict[str, AgentSkillScore]:
    return {
        "spoken_keyword": AgentSkillScore(
            score=spoken_keyword_score,
            reason="Estimated from supplied transcript/script matching niche keywords.",
            suggestions=["Say the main niche keyword naturally in the first line."],
        ),
        "on_screen_keyword": AgentSkillScore(
            score=on_screen_keyword_score,
            reason="On-screen OCR is not implemented yet, so this remains a low-confidence estimate.",
            suggestions=["Put the primary search phrase as visible text in the first 3 seconds."],
        ),
        "niche_query_match": AgentSkillScore(
            score=niche_query_match_score,
            reason="Estimated from overlap between provided niche and transcript/trend context.",
            suggestions=["Phrase the hook like a query your audience would search."],
        ),
        "search_intent_clarity": AgentSkillScore(
            score=search_intent_clarity_score,
            reason="Estimated from whether the supplied script or trend context clarifies the viewer intent.",
            suggestions=["Make the intended search/use case explicit before the payoff."],
        ),
    }
