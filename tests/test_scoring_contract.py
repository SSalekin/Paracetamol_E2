from backend.app.schemas.scoring import ViralScoreResponse


def test_viral_score_response_contract():
    payload = {
        "overall_score": 70,
        "hook_strength": {
            "score": 70,
            "explanation": "Good hook.",
            "actionable_fix": "Add stronger text overlay.",
        },
        "completion_rate": {
            "score": 60,
            "explanation": "Moderate retention.",
            "actionable_fix": "Cut dead air.",
        },
        "shares_saves_probability": {
            "score": 50,
            "explanation": "Limited utility.",
            "actionable_fix": "Add checklist value.",
        },
        "sound_trend_timing": {
            "score": 50,
            "explanation": "Trend unknown.",
            "actionable_fix": "Provide sound context.",
        },
        "search_keyword_relevance": {
            "score": 50,
            "explanation": "SEO unclear.",
            "actionable_fix": "Add niche keyword.",
        },
        "early_engagement_velocity": {
            "score": 50,
            "explanation": "Few engagement triggers.",
            "actionable_fix": "Add a specific question.",
        },
        "content_niche_fit": {
            "score": 70,
            "explanation": "Mostly aligned.",
            "actionable_fix": "Name the target audience.",
        },
        "retention_drop_zones": [],
        "predicted_reach_range": "Heuristic estimate.",
        "suggested_script_variant": None,
        "debug_trace": [],
    }

    parsed = ViralScoreResponse.model_validate(payload)

    assert parsed.overall_score == 70
