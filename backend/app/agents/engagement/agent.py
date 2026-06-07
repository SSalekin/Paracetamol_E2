from backend.app.agents.engagement.skills import build_engagement_skills
from backend.app.agents.common import run_intelligent_agent
from backend.app.schemas.scoring import AgentResult


ENGAGEMENT_SYSTEM_PROMPT = """You are the Early Engagement Velocity Agent.
Judge whether the video is likely to trigger early comments, reactions, debate, replay, or fast watch signals.

Return only valid JSON matching this shape:
{
  "name": "early_engagement_velocity",
  "score": 0,
  "summary": "",
  "reason": "",
  "actionable_tips": [],
  "skills": {
    "comment_trigger": {"score": 0, "reason": "", "suggestions": []},
    "curiosity_loop": {"score": 0, "reason": "", "suggestions": []},
    "debate_potential": {"score": 0, "reason": "", "suggestions": []},
    "replay_trigger": {"score": 0, "reason": "", "suggestions": []}
  },
  "extra": {}
}

Avoid generic engagement advice. Give a specific prompt or structural change."""


def build_engagement_fallback(state_data: dict) -> AgentResult:
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


async def run_engagement_agent(state_data: dict) -> AgentResult:
    return await run_intelligent_agent(
        agent_name="engagement_agent",
        system_prompt=ENGAGEMENT_SYSTEM_PROMPT,
        state_data=state_data,
        fallback_result=build_engagement_fallback(state_data),
        focus="Evaluate comment trigger, curiosity loop, debate potential, replay trigger, and early engagement velocity.",
    )
