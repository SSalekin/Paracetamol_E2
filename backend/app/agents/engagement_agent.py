from backend.app.schemas.scoring import AgentResult, AgentSkillScore


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
        skills={
            "comment_trigger": AgentSkillScore(
                score=75 if has_comment_prompt else 55,
                reason="Estimated from explicit comment or viewer-choice prompts.",
                suggestions=["Ask a specific low-friction question tied to the content."],
            ),
            "curiosity_loop": AgentSkillScore(
                score=75 if has_curiosity_loop or has_question else 55,
                reason="Estimated from question marks, guessing prompts, or continuation loops.",
                suggestions=["Open a specific curiosity gap that resolves after the payoff."],
            ),
            "debate_potential": AgentSkillScore(
                score=70 if "do you agree" in matched else 55,
                reason="Estimated from whether the script invites disagreement or comparison.",
                suggestions=["Turn the claim into a specific choice or opinion prompt."],
            ),
            "replay_trigger": AgentSkillScore(
                score=60 if has_curiosity_loop else 55,
                reason="Replay triggers are hard to verify without full video structure; estimated from curiosity loop terms.",
                suggestions=["Add a fast visual detail viewers may need to rewatch."],
            ),
        },
        extra={
            "matched_triggers": matched,
            "heuristic_only": True,
            "confidence": "medium" if matched else "low",
        },
    )
