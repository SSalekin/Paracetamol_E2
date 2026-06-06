from typing import Any, TypedDict


class VideoScoreGraphState(TypedDict, total=False):
    # Input
    video_path: str
    niche: str
    audience: str
    posting_time: str
    full_transcript: str
    trend_context: str

    # Extracted signals
    hook_frames_b64: list[str]
    visual_features: dict[str, Any]
    text_script: str
    actual_video_context: str
    alignment_score: float

    # Agent outputs
    agent_results: dict[str, Any]

    # Final output
    final_score: Any
    debug_trace: list[str]
