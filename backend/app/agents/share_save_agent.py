from backend.app.schemas.scoring import AgentResult


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

    return AgentResult(
        name="shares_saves_probability",
        score=score,
        summary=f"Share/save score {score}/100",
        reason=reason,
        actionable_tips=tips,
        skills={},
        extra={
            "matched_triggers": matched,
            "heuristic_only": True,
            "confidence": "medium" if matched else "low",
        },
    )
