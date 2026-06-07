from pydantic import BaseModel, Field


class HookJudgeInput(BaseModel):
    curiosity_gap: int = Field(..., ge=0, le=100)
    opening_text: int = Field(..., ge=0, le=100)
    visual_shock: int = Field(..., ge=0, le=100)


class HookJudgeOutput(BaseModel):
    hook_score: int = Field(..., ge=0, le=100)
    hook_score_raw: int = Field(..., ge=0, le=100)


def judge_hook(payload: HookJudgeInput) -> HookJudgeOutput:
    raw = round(
        (0.50 * payload.curiosity_gap)
        + (0.30 * payload.opening_text)
        + (0.20 * payload.visual_shock)
    )

    value = round(raw * 0.85 + 10)
    if value < 10:
        value = 10
    if value > 100:
        value = 100

    return HookJudgeOutput(hook_score=value, hook_score_raw=raw)

