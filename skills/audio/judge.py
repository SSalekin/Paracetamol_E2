from pydantic import BaseModel, Field


class AudioJudgeInput(BaseModel):
    audio_clarity: int = Field(..., ge=0, le=100)
    audio_trend_fit: int = Field(..., ge=0, le=100)


class AudioJudgeOutput(BaseModel):
    audio_score: int = Field(..., ge=0, le=100)
    audio_score_raw: int = Field(..., ge=0, le=100)


def judge_audio(payload: AudioJudgeInput) -> AudioJudgeOutput:
    raw = round(0.55 * payload.audio_clarity + 0.45 * payload.audio_trend_fit)
    value = round(raw * 0.9 + 8)
    if value < 10:
        value = 10
    if value > 100:
        value = 100
    return AudioJudgeOutput(audio_score=value, audio_score_raw=raw)

