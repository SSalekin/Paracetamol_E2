from backend.app.schemas.scoring import AgentResult


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

    score = min(85, 35 + keyword_hits * 15)

    return AgentResult(
        name="search_keyword_relevance",
        score=score,
        summary=f"SEO relevance score {score}/100",
        reason="SEO score is based on niche keyword presence and supplied trend context.",
        actionable_tips=[
            "Add the main niche keyword as spoken audio and on-screen text within the first 3 seconds."
        ],
        skills={},
        extra={
            "keyword_hits": keyword_hits,
        },
    )
