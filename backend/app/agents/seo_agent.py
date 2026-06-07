from backend.app.schemas.scoring import AgentResult, AgentSkillScore


async def run_seo_agent(state_data: dict) -> AgentResult:
    niche = state_data.get("niche", "").lower()
    text = state_data.get("text_script", "").lower()
    trend_context = state_data.get("trend_context", "").lower()

    keyword_hits = 0

    for token in niche.split():
        if len(token) > 3 and token in text:
            keyword_hits += 1

    if trend_context and trend_context != "live audio and keyword trend context was not provided.":
        keyword_hits += 1

    score = min(85, 55 + keyword_hits * 10)
    has_text = bool(text and text != "transcript was not provided.")
    has_trend_context = bool(
        trend_context
        and "not provided" not in trend_context
    )

    return AgentResult(
        name="search_keyword_relevance",
        score=score,
        summary=f"SEO relevance score {score}/100",
        reason="SEO score is based on niche keyword presence and supplied trend context. This should not strongly penalize visual-first videos when transcript or on-screen OCR is unavailable.",
        actionable_tips=[
            "Add the main niche keyword as spoken audio and on-screen text within the first 3 seconds."
        ],
        skills={
            "spoken_keyword": AgentSkillScore(
                score=70 if keyword_hits else 55,
                reason="Estimated from supplied transcript/script matching niche keywords.",
                suggestions=["Say the main niche keyword naturally in the first line."],
            ),
            "on_screen_keyword": AgentSkillScore(
                score=55,
                reason="On-screen OCR is not implemented yet, so this remains a low-confidence estimate.",
                suggestions=["Put the primary search phrase as visible text in the first 3 seconds."],
            ),
            "niche_query_match": AgentSkillScore(
                score=70 if keyword_hits else 55,
                reason="Estimated from overlap between provided niche and transcript/trend context.",
                suggestions=["Phrase the hook like a query your audience would search."],
            ),
            "search_intent_clarity": AgentSkillScore(
                score=65 if has_text or has_trend_context else 55,
                reason="Estimated from whether the supplied script or trend context clarifies the viewer intent.",
                suggestions=["Make the intended search/use case explicit before the payoff."],
            ),
        },
        extra={
            "keyword_hits": keyword_hits,
            "heuristic_only": True,
            "confidence": "medium" if keyword_hits else "low",
        },
    )
