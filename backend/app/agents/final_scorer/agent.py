from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.agents.final_scorer.prompts import FINAL_SCORER_SYSTEM_PROMPT
from backend.app.agents.final_scorer.utils import (
    build_user_text,
    extract_json,
    image_payload,
)
from backend.app.core.llm import get_llm
from backend.app.schemas.scoring import ViralScoreResponse


async def run_final_scorer_agent(state_data: dict[str, Any]) -> ViralScoreResponse:
    llm = get_llm()

    user_content = [
        {"type": "text", "text": build_user_text(state_data)},
        *image_payload(state_data.get("hook_frames_b64", [])),
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

    payload = extract_json(raw_content)
    final_score = ViralScoreResponse.model_validate(payload)
    final_score.debug_trace = list(state_data.get("debug_trace", []))

    return final_score
