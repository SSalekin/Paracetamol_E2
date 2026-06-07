from backend.app.schemas.scoring import AgentSkillScore


def build_share_save_skills(
    *,
    utility_score: int,
    emotional_score: int,
    identity_score: int,
    save_prompt_score: int,
) -> dict[str, AgentSkillScore]:
    return {
        "utility_value": AgentSkillScore(
            score=utility_score,
            reason="Estimated from explicit utility words such as how-to, tips, checklist, or before-you framing.",
            suggestions=["Make the practical value visible as text in the first second."],
        ),
        "emotional_trigger": AgentSkillScore(
            score=emotional_score,
            reason="Estimated from warning, mistake, secret, or avoidance language.",
            suggestions=["Frame the stakes more sharply: what happens if the viewer ignores this?"],
        ),
        "identity_shareability": AgentSkillScore(
            score=identity_score,
            reason="Identity shareability needs visual/audience evidence beyond simple script keyword matching.",
            suggestions=["Call out the exact viewer identity or situation in the opening."],
        ),
        "save_prompt_strength": AgentSkillScore(
            score=save_prompt_score,
            reason="Estimated from whether the script explicitly gives a reason to save.",
            suggestions=["Use a specific save prompt, for example: 'Save this before you buy...'"],
        ),
    }
