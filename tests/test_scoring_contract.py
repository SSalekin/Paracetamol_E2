from backend.app.schemas.scoring import ViralScoreResponse
from backend.app.extractors.visual_extractor import extract_hook_frames
from backend.app.core.aggregator import aggregate_score
from backend.app.agents.engagement import run_engagement_agent
from backend.app.agents.niche_fit import run_niche_fit_agent
from backend.app.agents.retention import run_retention_agent
from backend.app.agents.seo import run_seo_agent
from backend.app.agents.share_save import run_share_save_agent
from backend.app.agents.trend import run_trend_agent
from backend.app.extractors.transcript_extractor import extract_text_script


def test_hook_frame_extraction_samples_three_frames_per_second(tmp_path):
    import cv2
    import numpy as np

    video_path = tmp_path / "sample.mp4"
    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        6,
        (64, 64),
    )

    for index in range(20):
        writer.write(
            np.full(
                (64, 64, 3),
                index * 10 % 255,
                dtype=np.uint8,
            )
        )

    writer.release()

    frames = extract_hook_frames(str(video_path), seconds=3, frames_per_second=3)

    assert len(frames) == 9
    assert all(isinstance(frame, str) and frame for frame in frames)


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


def test_fallback_aggregator_does_not_over_penalize_low_confidence_context_gaps():
    score = aggregate_score(
        {
            "debug_trace": [],
            "agent_results": {
                "hook_strength": {
                    "score": 78,
                    "reason": "Strong first-frame visual disruption and clear premise.",
                    "actionable_tips": ["Tighten the first overlay to six words."],
                    "extra": {},
                },
                "completion_rate": {
                    "score": 70,
                    "reason": "Short video with acceptable retention risk.",
                    "actionable_tips": ["Avoid adding an outro."],
                    "extra": {},
                },
                "shares_saves_probability": {
                    "score": 55,
                    "reason": "No explicit text trigger found.",
                    "actionable_tips": ["Add a save-worthy promise."],
                    "extra": {"heuristic_only": True, "confidence": "low"},
                },
                "sound_trend_timing": {
                    "score": 60,
                    "reason": "Trend context missing.",
                    "actionable_tips": ["Provide sound context."],
                    "extra": {"heuristic_only": True, "confidence": "low"},
                },
                "search_keyword_relevance": {
                    "score": 55,
                    "reason": "SEO context missing.",
                    "actionable_tips": ["Add a niche keyword."],
                    "extra": {"heuristic_only": True, "confidence": "low"},
                },
                "early_engagement_velocity": {
                    "score": 55,
                    "reason": "No explicit comment trigger found.",
                    "actionable_tips": ["Add a low-friction prompt."],
                    "extra": {"heuristic_only": True, "confidence": "low"},
                },
                "content_niche_fit": {
                    "score": 70,
                    "reason": "Mostly aligned with the provided niche.",
                    "actionable_tips": ["Name the target viewer earlier."],
                    "extra": {},
                },
            },
        }
    )

    assert score.overall_score >= 68


async def _collect_skill_agents():
    state = {
        "text_script": "How to avoid this mistake? Save this checklist and comment which one you would use.",
        "trend_context": "Trending sound is rising this week.",
        "niche": "skincare tips",
        "audience": "students",
        "visual_features": {
            "duration_seconds": 8,
            "pacing_rate": 1.2,
        },
    }

    return {
        "retention": await run_retention_agent(state),
        "share_save": await run_share_save_agent(state),
        "seo": await run_seo_agent(state),
        "trend": await run_trend_agent(state),
        "engagement": await run_engagement_agent(state),
        "niche_fit": await run_niche_fit_agent(state),
    }


def test_non_hook_agents_emit_skill_breakdowns(monkeypatch):
    import asyncio

    monkeypatch.setenv("AGENT_LLM_ENABLED", "false")

    results = asyncio.run(_collect_skill_agents())

    assert set(results["retention"].skills) == {
        "opening_pacing",
        "payoff_preview",
        "dropoff_risk",
        "ending_drag",
    }
    assert set(results["share_save"].skills) == {
        "utility_value",
        "emotional_trigger",
        "identity_shareability",
        "save_prompt_strength",
    }
    assert set(results["seo"].skills) == {
        "spoken_keyword",
        "on_screen_keyword",
        "niche_query_match",
        "search_intent_clarity",
    }
    assert set(results["trend"].skills) == {
        "trend_context_available",
        "sound_freshness",
        "audio_visual_sync",
        "trend_fit",
    }
    assert set(results["engagement"].skills) == {
        "comment_trigger",
        "curiosity_loop",
        "debate_potential",
        "replay_trigger",
    }
    assert set(results["niche_fit"].skills) == {
        "audience_clarity",
        "niche_relevance",
        "brand_consistency",
        "viewer_problem_match",
    }


def test_manual_transcript_takes_precedence_over_whisper(monkeypatch):
    import asyncio

    monkeypatch.setenv("WHISPER_PROVIDER", "disabled")

    transcript = asyncio.run(
        extract_text_script(
            video_path="/does/not/matter.mp4",
            provided_transcript="User supplied transcript",
            fallback_text="Fallback text",
        )
    )

    assert transcript == "User supplied transcript"


def test_transcript_extractor_falls_back_when_whisper_disabled(monkeypatch):
    import asyncio

    monkeypatch.setenv("WHISPER_PROVIDER", "disabled")

    transcript = asyncio.run(
        extract_text_script(
            video_path="/does/not/matter.mp4",
            provided_transcript=None,
            fallback_text="Fallback text",
        )
    )

    assert transcript == "Fallback text"
