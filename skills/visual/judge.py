from pydantic import BaseModel, Field


class VisualJudgeInput(BaseModel):
    clarity: int = Field(..., ge=0, le=100)
    composition: int = Field(..., ge=0, le=100)


class VisualJudgeOutput(BaseModel):
    visual_score: int = Field(..., ge=0, le=100)
    visual_score_raw: int = Field(..., ge=0, le=100)


def judge_visual(payload: VisualJudgeInput) -> VisualJudgeOutput:
    raw = round(0.55 * payload.clarity + 0.45 * payload.composition)
    value = round(raw * 0.9 + 8)
    if value < 10:
        value = 10
    if value > 100:
        value = 100
    return VisualJudgeOutput(visual_score=value, visual_score_raw=raw)

