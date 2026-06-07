from backend.app.agents.engagement.skills import build_engagement_skills
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

    score = min(85, 55 + len(matched) * 10)
    has_question = "?" in matched
    has_comment_prompt = any(trigger in matched for trigger in ["comment", "which one", "would you", "do you agree"])
    has_curiosity_loop = any(trigger in matched for trigger in ["part 2", "guess"])

    return AgentResult(
        name="early_engagement_velocity",
        score=score,
        summary=f"Engagement velocity score {score}/100",
        reason="Engagement velocity is estimated from comment prompts, curiosity loops, and question triggers. Treat this as heuristic-only because visual surprise can also drive early engagement.",
        actionable_tips=[
            "Add one low-friction comment prompt, not a generic 'comment below'."
        ],
        skills=build_engagement_skills(
            has_question=has_question,
            has_comment_prompt=has_comment_prompt,
            has_curiosity_loop=has_curiosity_loop,
            has_debate_prompt="do you agree" in matched,
        ),
        extra={
            "matched_triggers": matched,
            "heuristic_only": True,
            "confidence": "medium" if matched else "low",
        },
    )
