from pydantic import BaseModel, Field


class TrendJudgeInput(BaseModel):
    trend_topic: int = Field(..., ge=0, le=100)
    trend_format: int = Field(..., ge=0, le=100)


class TrendJudgeOutput(BaseModel):
    trend_score: int = Field(..., ge=0, le=100)
    trend_score_raw: int = Field(..., ge=0, le=100)


def judge_trend(payload: TrendJudgeInput) -> TrendJudgeOutput:
    raw = round(0.60 * payload.trend_topic + 0.40 * payload.trend_format)
    value = round(raw * 0.9 + 8)
    if value < 10:
        value = 10
    if value > 100:
        value = 100
    return TrendJudgeOutput(trend_score=value, trend_score_raw=raw)

