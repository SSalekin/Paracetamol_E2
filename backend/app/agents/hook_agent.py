from typing import Any

from backend.app.schemas.scoring import AgentResult, AgentSkillScore


async def run_hook_agent(state_data: dict[str, Any]) -> AgentResult:
    visual_features = state_data.get("visual_features", {})
    text = (state_data.get("text_script") or "").strip()
    hook_frames = state_data.get("hook_frames_b64", [])

    hook_intensity = float(visual_features.get("hook_intensity") or 0)
    pacing_rate = float(visual_features.get("pacing_rate") or 0)

    visual_disruption_score = min(90, 55 + int(hook_intensity * 1.2) + int(pacing_rate * 8))
    specificity_score = 70 if text and text != "Transcript was not provided." else 55
    curiosity_score = 72 if any(token in text.lower() for token in ["?", "secret", "mistake", "why", "how"]) else 58
    scroll_stop_score = 72 if len(hook_frames) >= 9 else 62

    score = round(
        scroll_stop_score * 0.30
        + specificity_score * 0.25
        + curiosity_score * 0.20
        + visual_disruption_score * 0.25
    )

    if hook_intensity < 5 and pacing_rate < 0.5:
        reason = "Opening hook appears visually calm from OpenCV motion/cut signals; final visual judgment is deferred to the final multimodal scorer."
        tips = ["Add a visible change, zoom, cut, or text overlay inside the first second."]
    else:
        reason = "Opening has enough visual or pacing signal to be a plausible scroll-stop hook; final visual judgment is deferred to the final multimodal scorer."
        tips = ["Make the first on-screen text state the payoff in six words or fewer."]

    return AgentResult(
        name="hook_strength",
        score=score,
        summary=f"Local hook diagnostic score {score}/100",
        reason=reason,
        actionable_tips=tips,
        skills={
            "scroll_stop": AgentSkillScore(
                score=scroll_stop_score,
                reason="Estimated from available first-three-second frame samples.",
                suggestions=["Keep the strongest visual contrast in the first frame."],
            ),
            "specificity": AgentSkillScore(
                score=specificity_score,
                reason="Estimated from whether usable transcript/script context exists.",
                suggestions=["Name the specific outcome or target viewer immediately."],
            ),
            "curiosity_gap": AgentSkillScore(
                score=curiosity_score,
                reason="Estimated from script/question/curiosity trigger terms.",
                suggestions=["Open a clear information gap before explaining."],
            ),
            "visual_disruption": AgentSkillScore(
                score=visual_disruption_score,
                reason="Estimated from OpenCV motion and scene-cut features.",
                suggestions=["Add a pattern break in the first second if the opening is static."],
            ),
        },
        extra={
            "heuristic_only": True,
            "confidence": "medium",
            "hook_intensity": hook_intensity,
            "pacing_rate": pacing_rate,
            "frame_count": len(hook_frames),
        },
    )
