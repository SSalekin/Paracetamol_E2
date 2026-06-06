from typing import Any

from backend.app.schemas.scoring import (
    DimensionScore,
    RetentionDropZone,
    ViralScoreResponse,
)

def _reach_range_from_score(score: int) -> str:
    if score >= 85:
        return "Heuristic estimate: high potential, but actual reach depends on account history, timing, and platform distribution."
    if score >= 70:
        return "Heuristic estimate: moderate-to-high potential."
    if score >= 50:
        return "Heuristic estimate: moderate potential."
    return "Heuristic estimate: low potential unless the hook and retention are improved."


def _script_variant_from_agents(agent_results: dict[str, Any]) -> str | None:
    hook = agent_results.get("hook_strength")

    if not hook:
        return None

    tips = hook.get("actionable_tips") or []

    if not tips:
        return None

    return f"Rewrite the opening around this fix: {tips[0]}"


def _dimension_from_agent(
    agent_result: dict[str, Any] | None,
    fallback_name: str,
) -> DimensionScore:
    if not agent_result:
        return DimensionScore(
            score=50,
            explanation=f"{fallback_name} was not evaluated by a dedicated agent.",
            actionable_fix="Add a dedicated agent for this dimension.",
        )

    tips = agent_result.get("actionable_tips") or []

    return DimensionScore(
        score=int(agent_result.get("score", 50)),
        explanation=agent_result.get("reason") or agent_result.get("summary") or "",
        actionable_fix=tips[0] if tips else "No concrete fix was provided.",
    )

def _score(agent_results: dict[str, Any], key: str, default: int = 50) -> int:
    result = agent_results.get(key)

    if not result:
        return default

    return int(result.get("score", default))


def aggregate_score(state_data: dict[str, Any]) -> ViralScoreResponse:
    agent_results = state_data.get("agent_results", {})
    debug_trace = list(state_data.get("debug_trace", []))
    debug_trace.append("aggregator:complete")

    hook = agent_results.get("hook_strength")
    completion = agent_results.get("completion_rate")
    share_save = agent_results.get("shares_saves_probability")
    trend = agent_results.get("sound_trend_timing")
    seo = agent_results.get("search_keyword_relevance")
    engagement = agent_results.get("early_engagement_velocity")
    niche_fit = agent_results.get("content_niche_fit")

    weights = {
        "hook_strength": 0.30,
        "completion_rate": 0.25,
        "shares_saves_probability": 0.15,
        "sound_trend_timing": 0.10,
        "search_keyword_relevance": 0.10,
        "early_engagement_velocity": 0.05,
        "content_niche_fit": 0.05,
    }

    overall_score = round(
        _score(agent_results, "hook_strength") * weights["hook_strength"]
        + _score(agent_results, "completion_rate") * weights["completion_rate"]
        + _score(agent_results, "shares_saves_probability") * weights["shares_saves_probability"]
        + _score(agent_results, "sound_trend_timing") * weights["sound_trend_timing"]
        + _score(agent_results, "search_keyword_relevance") * weights["search_keyword_relevance"]
        + _score(agent_results, "early_engagement_velocity") * weights["early_engagement_velocity"]
        + _score(agent_results, "content_niche_fit") * weights["content_niche_fit"]
    )

    return ViralScoreResponse(
        overall_score=overall_score,

        hook_strength=_dimension_from_agent(hook, "Hook strength"),
        completion_rate=_dimension_from_agent(completion, "Completion rate"),
        shares_saves_probability=_dimension_from_agent(share_save, "Share/save probability"),
        sound_trend_timing=_dimension_from_agent(trend, "Sound trend timing"),
        search_keyword_relevance=_dimension_from_agent(seo, "Search keyword relevance"),
        early_engagement_velocity=_dimension_from_agent(engagement, "Early engagement velocity"),
        content_niche_fit=_dimension_from_agent(niche_fit, "Content niche fit"),

        retention_drop_zones=[
            RetentionDropZone(
                timestamp_range="00:00 - 00:04",
                reason=completion.get("reason", "Retention risk estimated from opening pacing."),
                severity="Medium" if _score(agent_results, "completion_rate") < 70 else "Low",
            )
        ],

        predicted_reach_range=_reach_range_from_score(overall_score),
        suggested_script_variant=_script_variant_from_agents(agent_results),
        debug_trace=debug_trace,
    )
