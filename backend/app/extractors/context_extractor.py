def extract_context(
    trend_context: str | None,
    niche: str,
    audience: str,
) -> dict[str, object]:
    usable_trend_context = (
        trend_context.strip()
        if trend_context and trend_context.strip()
        else "Live trend context was not provided."
    )

    return {
        "actual_video_context": (
            f"Niche: {niche}. Audience: {audience}. "
            f"Trend context: {usable_trend_context}"
        ),
        "alignment_score": 0.0,
    }
