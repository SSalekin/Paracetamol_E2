from backend.app.schemas.scoring import AgentResult, AgentSkillScore


async def run_share_save_agent(state_data: dict) -> AgentResult:
    text = state_data.get("text_script", "").lower()

    value_words = [
        "how to",
        "mistake",
        "secret",
        "save",
        "checklist",
        "tips",
        "avoid",
        "before you",
    ]

    matched = [word for word in value_words if word in text]

    score = min(90, 55 + len(matched) * 10)

    if not matched:
        reason = "No explicit save/share trigger was found in the supplied script text. This is a medium-confidence heuristic because visual identity, product desirability, or emotional framing may still create share value."
        tips = ["Add a specific promise such as: 'Save this before you buy...' or 'Avoid this mistake...'"]
    else:
        reason = f"The script contains save/share triggers: {', '.join(matched)}."
        tips = ["Make the value promise visible as on-screen text in the first second."]

    utility_score = 70 if any(word in matched for word in ["how to", "tips", "checklist"]) else 55
    emotional_score = 70 if any(word in matched for word in ["mistake", "secret", "avoid"]) else 55
    identity_score = 60
    save_prompt_score = 75 if "save" in matched else 55

    return AgentResult(
        name="shares_saves_probability",
        score=score,
        summary=f"Share/save score {score}/100",
        reason=reason,
        actionable_tips=tips,
        skills={
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
        },
        extra={
            "matched_triggers": matched,
            "heuristic_only": True,
            "confidence": "medium" if matched else "low",
        },
    )
