from pydantic import BaseModel, Field


class RetentionJudgeInput(BaseModel):
    pacing: int = Field(..., ge=0, le=100)
    attention_decay: int = Field(..., ge=0, le=100)


class RetentionJudgeOutput(BaseModel):
    retention_score: int = Field(..., ge=0, le=100)
    retention_score_raw: int = Field(..., ge=0, le=100)


def judge_retention(payload: RetentionJudgeInput) -> RetentionJudgeOutput:
    raw = round(0.55 * payload.pacing + 0.45 * payload.attention_decay)
    value = round(raw * 0.9 + 8)
    if value < 10:
        value = 10
    if value > 100:
        value = 100
    return RetentionJudgeOutput(retention_score=value, retention_score_raw=raw)

