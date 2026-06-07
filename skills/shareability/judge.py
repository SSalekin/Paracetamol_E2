from pydantic import BaseModel, Field


class ShareabilityJudgeInput(BaseModel):
    value_density: int = Field(..., ge=0, le=100)
    save_share_cta: int = Field(..., ge=0, le=100)


class ShareabilityJudgeOutput(BaseModel):
    shareability_score: int = Field(..., ge=0, le=100)
    shareability_score_raw: int = Field(..., ge=0, le=100)


def judge_shareability(payload: ShareabilityJudgeInput) -> ShareabilityJudgeOutput:
    raw = round(0.65 * payload.value_density + 0.35 * payload.save_share_cta)
    value = round(raw * 0.9 + 8)
    if value < 10:
        value = 10
    if value > 100:
        value = 100
    return ShareabilityJudgeOutput(shareability_score=value, shareability_score_raw=raw)

