import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.core.llm import get_llm
from backend.app.schemas.scoring import ViralScoreResponse


FINAL_SCORER_SYSTEM_PROMPT = """You are the final evaluation brain of the ViralScore engine for the AI Hackathon 2026.
Your job is to act as an elite TikTok growth strategist inspecting short-form content before publication.
You must synthesize specialist agent findings, transcript/context, OpenCV visual features, and sampled hook frames into one useful scoring report.
The specialist agent scores are advisory diagnostics, not binding grades. Some agents are lightweight heuristics and can under-score when transcript, audio trend data, or keyword context is missing. Your final score must be calibrated from the raw video evidence and metadata first, then use specialist findings to explain or refine the judgment.

You evaluate videos against strict algorithmic constraints where the completion threshold is now 70%.

Critical evaluation criteria:
- Hook Strength: Analyze visual disruption, overlays, first-frame clarity, and opening script. Deduct points for generic introductions.
- Completion Rate: Identify likely drop zones. Look for slow openings, weak payoff preview, and outro/drop-off traps.
- Shares/Saves Probability: Reward concrete utility, identity value, controversy, checklist value, and emotional share triggers.
- Sound Trend Timing: Use supplied trend context when available. If missing, explicitly state what cannot be verified.
- Search Keyword Relevance: Check whether the niche/search phrase is visible, spoken, or structurally implied early.
- Early Engagement Velocity: Evaluate whether the content invites comments, debate, repeat views, or fast reactions without generic bait.
- Content Niche Fit: Judge whether the content is aligned with the target niche/audience and whether the first seconds make that audience obvious.

Scoring calibration:
- 85-100: Exceptional viral mechanics; strong scroll-stop hook, clear payoff, strong share/save trigger, and clear niche fit.
- 70-84: Strong pre-publication candidate; clear hook or visual disruption plus enough retention/value evidence, even if trend or SEO data is incomplete.
- 50-69: Mixed candidate; some useful elements, but hook/retention/value are not consistently strong.
- 0-49: Weak candidate; generic opening, unclear payoff, low pacing, or little audience/value signal.

Do not push the overall score below 70 only because sound trend, transcript, or SEO context is missing. Missing context should create uncertainty in that dimension, not erase strong visual hook evidence.

Actionable fixes must be concrete. Never write generic advice like "make it more engaging".
Tell the user exactly where to cut, what text to overlay, what opening words to use, or what visual change to make.

Return only valid JSON matching this exact object shape:
{
  "overall_score": 0,
  "hook_strength": {"score": 0, "explanation": "", "actionable_fix": ""},
  "completion_rate": {"score": 0, "explanation": "", "actionable_fix": ""},
  "shares_saves_probability": {"score": 0, "explanation": "", "actionable_fix": ""},
  "sound_trend_timing": {"score": 0, "explanation": "", "actionable_fix": ""},
  "search_keyword_relevance": {"score": 0, "explanation": "", "actionable_fix": ""},
  "early_engagement_velocity": {"score": 0, "explanation": "", "actionable_fix": ""},
  "content_niche_fit": {"score": 0, "explanation": "", "actionable_fix": ""},
  "retention_drop_zones": [{"timestamp_range": "", "reason": "", "severity": ""}],
  "predicted_reach_range": "",
  "suggested_script_variant": ""
}"""


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    if "```" in text:
        lines = [
            line
            for line in text.splitlines()
            if not line.strip().startswith("```")
        ]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Final scorer response did not contain JSON.")

    return json.loads(text[start : end + 1])


def _image_payload(frames_b64: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_b64}",
            },
        }
        for frame_b64 in frames_b64
    ]


def _build_user_text(state_data: dict[str, Any]) -> str:
    return f"""--- METADATA ---
Target Niche: {state_data.get("niche")}
Target Audience: {state_data.get("audience")}
Planned Posting Time: {state_data.get("posting_time")}

--- TRANSCRIPT / SCRIPT ---
{state_data.get("text_script")}

--- LIVE TREND / KEYWORD CONTEXT ---
{state_data.get("trend_context")}

--- ACTUAL VIDEO CONTEXT ---
{state_data.get("actual_video_context")}

--- OPENCV VISUAL FEATURES ---
{state_data.get("visual_features")}

--- SPECIALIST AGENT FINDINGS ---
{json.dumps(state_data.get("agent_results", {}), ensure_ascii=False, indent=2)}

Important: the specialist findings above are advisory. If an agent says "heuristic_only" or "confidence: low", treat its numeric score as weak evidence. Do not average the specialist scores mechanically.

Produce a monolith-quality final report with specific explanations, concrete fixes, realistic retention drop zones, and a script variant that addresses the biggest weakness."""


async def run_final_scorer_agent(state_data: dict[str, Any]) -> ViralScoreResponse:
    llm = get_llm()

    user_content = [
        {"type": "text", "text": _build_user_text(state_data)},
        *_image_payload(state_data.get("hook_frames_b64", [])),
    ]

    response = await llm.ainvoke(
        [
            SystemMessage(content=FINAL_SCORER_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
    )

    raw_content = getattr(response, "content", response)

    if not isinstance(raw_content, str):
        raw_content = str(raw_content)

    payload = _extract_json(raw_content)
    final_score = ViralScoreResponse.model_validate(payload)
    final_score.debug_trace = list(state_data.get("debug_trace", []))

    return final_score
