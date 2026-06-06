from backend.app.schemas.scoring import AgentResult


async def run_engagement_agent(state_data: dict) -> AgentResult:
    text = state_data.get("text_script", "").lower()

    engagement_triggers = [
        "?",
        "comment",
        "which one",
        "would you",
        "do you agree",
        "part 2",
        "guess",
    ]

    matched = [trigger for trigger in engagement_triggers if trigger in text]

    score = min(85, 40 + len(matched) * 12)

    return AgentResult(
        name="early_engagement_velocity",
        score=score,
        summary=f"Engagement velocity score {score}/100",
        reason="Engagement velocity is estimated from comment prompts, curiosity loops, and question triggers.",
        actionable_tips=[
            "Add one low-friction comment prompt, not a generic 'comment below'."
        ],
        skills={},
        extra={
            "matched_triggers": matched,
        },
    )
