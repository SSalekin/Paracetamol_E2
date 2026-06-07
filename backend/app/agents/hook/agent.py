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
    "curiosity": {"score": 0, "reason": "", "suggestions": []},
    "emotion": {"score": 0, "reason": "", "suggestions": []},
    "audience_fit": {"score": 0, "reason": "", "suggestions": []},
    "cta_engagement": {"score": 0, "reason": "", "suggestions": []},
    "pattern_match": {"score": 0, "reason": "", "suggestions": []},
    "retention_predictor": {"score": 0, "reason": "", "suggestions": []},
    "rewrite": {"score": 0, "reason": "", "suggestions": []},
    "sound_pacing": {"score": 0, "reason": "", "suggestions": []},
    "structure": {"score": 0, "reason": "", "suggestions": []},
    "visual_hook": {"score": 0, "reason": "", "suggestions": []},
    "curiosity_gap": {"score": 0, "reason": "", "suggestions": []},
    "visual_disruption": {"score": 0, "reason": "", "suggestions": []}
  },
  "extra": {}
}

Analyze frame clarity, visual disruption, first-frame readability, opening text/script specificity, curiosity, emotion, audience fit, CTA strength, hook pattern, retention prediction, rewrite opportunity, sound pacing, and structure. Give exact first-second fixes."""


def build_hook_fallback(state_data: dict[str, Any]) -> AgentResult:
    visual_features = state_data.get("visual_features", {})
    text = (state_data.get("text_script") or "").strip()
    hook_frames = state_data.get("hook_frames_b64", [])

    hook_intensity = float(visual_features.get("hook_intensity") or 0)
    pacing_rate = float(visual_features.get("pacing_rate") or 0)

    skills = build_hook_skills(
        text=text,
        niche=state_data.get("niche"),
        audience=state_data.get("audience"),
        hook_intensity=hook_intensity,
        pacing_rate=pacing_rate,
        frame_count=len(hook_frames),
    )

    score = round(
        skills["scroll_stop"].score * 0.22
        + skills["specificity"].score * 0.16
        + skills["curiosity"].score * 0.16
        + skills["emotion"].score * 0.10
        + skills["visual_hook"].score * 0.18
        + skills["structure"].score * 0.10
        + skills["audience_fit"].score * 0.08
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
        skills=skills,
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
        focus="Evaluate hook strength using scroll stop, specificity, curiosity, emotion, audience fit, CTA engagement, hook pattern match, retention prediction, rewrite quality, sound pacing, structure, and visual hook from the first 3 seconds.",
        include_hook_frames=True,
    )
