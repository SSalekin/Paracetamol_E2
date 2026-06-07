from typing import Any

from backend.app.agents.common import run_intelligent_agent
from backend.app.agents.hook.skills import build_hook_skills
from backend.app.schemas.scoring import AgentResult


HOOK_SYSTEM_PROMPT = """You are the Hook Strength Agent.
Judge only the first 3 seconds of the short-form video using sampled hook frames, transcript, niche/audience, and OpenCV visual features.

Return only valid JSON matching this shape:
{
  "name": "hook_strength",
  "score": 0,
  "summary": "",
  "reason": "",
  "actionable_tips": [],
  "skills": {
    "scroll_stop": {"score": 0, "reason": "", "suggestions": []},
    "specificity": {"score": 0, "reason": "", "suggestions": []},
    "curiosity_gap": {"score": 0, "reason": "", "suggestions": []},
    "visual_disruption": {"score": 0, "reason": "", "suggestions": []}
  },
  "extra": {}
}

Analyze frame clarity, visual disruption, first-frame readability, opening text/script specificity, and whether viewers have a reason to keep watching. Give exact first-second fixes."""


def build_hook_fallback(state_data: dict[str, Any]) -> AgentResult:
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
        skills=build_hook_skills(
            scroll_stop_score=scroll_stop_score,
            specificity_score=specificity_score,
            curiosity_score=curiosity_score,
            visual_disruption_score=visual_disruption_score,
        ),
        extra={
            "heuristic_only": True,
            "confidence": "medium",
            "hook_intensity": hook_intensity,
            "pacing_rate": pacing_rate,
            "frame_count": len(hook_frames),
        },
    )


async def run_hook_agent(state_data: dict[str, Any]) -> AgentResult:
    return await run_intelligent_agent(
        agent_name="hook_agent",
        system_prompt=HOOK_SYSTEM_PROMPT,
        state_data=state_data,
        fallback_result=build_hook_fallback(state_data),
        focus="Evaluate hook strength, scroll stop, specificity, curiosity gap, and visual disruption from the first 3 seconds.",
        include_hook_frames=True,
    )
