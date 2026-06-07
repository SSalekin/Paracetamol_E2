from backend.app.schemas.scoring import AgentSkillScore


def build_engagement_skills(
    *,
    has_question: bool,
    has_comment_prompt: bool,
    has_curiosity_loop: bool,
    has_debate_prompt: bool,
) -> dict[str, AgentSkillScore]:
    return {
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
            score=70 if has_debate_prompt else 55,
            reason="Estimated from whether the script invites disagreement or comparison.",
            suggestions=["Turn the claim into a specific choice or opinion prompt."],
        ),
        "replay_trigger": AgentSkillScore(
            score=60 if has_curiosity_loop else 55,
            reason="Replay triggers are hard to verify without full video structure; estimated from curiosity loop terms.",
            suggestions=["Add a fast visual detail viewers may need to rewatch."],
        ),
    }
