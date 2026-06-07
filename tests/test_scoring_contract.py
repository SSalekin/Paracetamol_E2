from backend.app.schemas.scoring import ViralScoreResponse
from backend.app.extractors.visual_extractor import extract_hook_frames
from backend.app.core.aggregator import aggregate_score


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
