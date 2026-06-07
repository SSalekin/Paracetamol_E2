from backend.app.agents.seo.skills import build_seo_skills
from backend.app.agents.common import run_intelligent_agent
from backend.app.schemas.scoring import AgentResult


SEO_SYSTEM_PROMPT = """You are the Search Keyword Relevance Agent.
Judge search discoverability for short-form platforms. Consider spoken keywords, likely on-screen keyword opportunity, niche query match, and search intent clarity.

Return only valid JSON matching this shape:
{
  "name": "search_keyword_relevance",
  "score": 0,
  "summary": "",
  "reason": "",
  "actionable_tips": [],
  "skills": {
    "spoken_keyword": {"score": 0, "reason": "", "suggestions": []},
    "on_screen_keyword": {"score": 0, "reason": "", "suggestions": []},
    "niche_query_match": {"score": 0, "reason": "", "suggestions": []},
    "search_intent_clarity": {"score": 0, "reason": "", "suggestions": []}
  },
  "extra": {}
}

Tell the creator exactly which words to say or overlay."""


def build_seo_fallback(state_data: dict) -> AgentResult:
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
        skills=build_seo_skills(
            spoken_keyword_score=70 if keyword_hits else 55,
            on_screen_keyword_score=55,
            niche_query_match_score=70 if keyword_hits else 55,
            search_intent_clarity_score=65 if has_text or has_trend_context else 55,
        ),
        extra={
            "keyword_hits": keyword_hits,
            "heuristic_only": True,
            "confidence": "medium" if keyword_hits else "low",
        },
    )


async def run_seo_agent(state_data: dict) -> AgentResult:
    return await run_intelligent_agent(
        agent_name="seo_agent",
        system_prompt=SEO_SYSTEM_PROMPT,
        state_data=state_data,
        fallback_result=build_seo_fallback(state_data),
        focus="Evaluate search keyword relevance, spoken keyword, on-screen keyword opportunity, niche query match, and search intent clarity.",
    )
