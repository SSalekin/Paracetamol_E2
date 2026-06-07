from pydantic import BaseModel, Field


class EngagementJudgeInput(BaseModel):
    emotion: int = Field(..., ge=0, le=100)
    relatability: int = Field(..., ge=0, le=100)


class EngagementJudgeOutput(BaseModel):
    engagement_score: int = Field(..., ge=0, le=100)
    engagement_score_raw: int = Field(..., ge=0, le=100)


def judge_engagement(payload: EngagementJudgeInput) -> EngagementJudgeOutput:
    raw = round(0.55 * payload.emotion + 0.45 * payload.relatability)
    value = round(raw * 0.9 + 8)
    if value < 10:
        value = 10
    if value > 100:
        value = 100
    return EngagementJudgeOutput(engagement_score=value, engagement_score_raw=raw)

