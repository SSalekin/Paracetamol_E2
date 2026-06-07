from backend.app.agents.niche_fit.skills import build_niche_fit_skills
from backend.app.agents.common import run_intelligent_agent
from backend.app.schemas.scoring import AgentResult


NICHE_FIT_SYSTEM_PROMPT = """You are the Content Niche Fit Agent.
Judge whether the video clearly fits the target niche and audience. Consider audience clarity, niche relevance, brand consistency, and viewer problem match.

Return only valid JSON matching this shape:
{
  "name": "content_niche_fit",
  "score": 0,
  "summary": "",
  "reason": "",
  "actionable_tips": [],
  "skills": {
    "audience_clarity": {"score": 0, "reason": "", "suggestions": []},
    "niche_relevance": {"score": 0, "reason": "", "suggestions": []},
    "brand_consistency": {"score": 0, "reason": "", "suggestions": []},
    "viewer_problem_match": {"score": 0, "reason": "", "suggestions": []}
  },
  "extra": {}
}

Be concrete about whether the first seconds make the intended viewer obvious."""


def build_niche_fit_fallback(state_data: dict) -> AgentResult:
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


async def run_niche_fit_agent(state_data: dict) -> AgentResult:
    return await run_intelligent_agent(
        agent_name="niche_fit_agent",
        system_prompt=NICHE_FIT_SYSTEM_PROMPT,
        state_data=state_data,
        fallback_result=build_niche_fit_fallback(state_data),
        focus="Evaluate audience clarity, niche relevance, brand consistency, viewer problem match, and content niche fit.",
    )
