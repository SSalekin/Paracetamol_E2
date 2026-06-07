import json
import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.core.llm import get_llm
from backend.app.schemas.scoring import AgentResult


def agent_llm_enabled() -> bool:
    return os.getenv("AGENT_LLM_ENABLED", "true").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
        "disabled",
    }


def extract_json(text: str, agent_name: str) -> dict[str, Any]:
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
        raise RuntimeError(f"{agent_name} response did not contain JSON.")

    return json.loads(text[start : end + 1])


def build_agent_user_text(state_data: dict[str, Any], focus: str) -> str:
    return f"""--- AGENT FOCUS ---
{focus}

--- METADATA ---
Target Niche: {state_data.get("niche")}
Target Audience: {state_data.get("audience")}
Planned Posting Time: {state_data.get("posting_time")}

--- TRANSCRIPT / SCRIPT ---
{state_data.get("text_script")}

--- TREND / KEYWORD CONTEXT ---
{state_data.get("trend_context")}

--- ACTUAL VIDEO CONTEXT ---
{state_data.get("actual_video_context")}

--- OPENCV VISUAL FEATURES ---
{state_data.get("visual_features")}

Return an AgentResult JSON object only. Every score must be 0-100. Make skill reasons and suggestions concrete."""


def image_payload(frames_b64: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_b64}",
            },
        }
        for frame_b64 in frames_b64
    ]


async def run_intelligent_agent(
    *,
    agent_name: str,
    system_prompt: str,
    state_data: dict[str, Any],
    fallback_result: AgentResult,
    focus: str,
    include_hook_frames: bool = False,
) -> AgentResult:
    if not agent_llm_enabled():
        fallback_result.extra = {
            **fallback_result.extra,
            "intelligence_mode": "heuristic_disabled",
        }
        return fallback_result

    try:
        user_content: str | list[dict[str, Any]]
        user_text = build_agent_user_text(state_data, focus)
        if include_hook_frames:
            user_content = [
                {"type": "text", "text": user_text},
                *image_payload(state_data.get("hook_frames_b64", [])),
            ]
        else:
            user_content = user_text

        response = await get_llm().ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_content),
            ]
        )
        raw_content = getattr(response, "content", response)
        if not isinstance(raw_content, str):
            raw_content = str(raw_content)

        result = AgentResult.model_validate(extract_json(raw_content, agent_name))
        result.extra = {
            **result.extra,
            "intelligence_mode": "llm",
        }
        return result
    except Exception as exc:
        fallback_result.extra = {
            **fallback_result.extra,
            "intelligence_mode": "heuristic_fallback",
            "llm_error": str(exc),
        }
        return fallback_result
