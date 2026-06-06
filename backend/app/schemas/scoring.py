from pydantic import BaseModel, Field
from typing import Optional, Any

class DimensionScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    explanation: str
    actionable_fix: str


class RetentionDropZone(BaseModel):
    timestamp_range: str
    reason: str
    severity: str


class ViralScoreResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)

    hook_strength: DimensionScore
    completion_rate: DimensionScore
    shares_saves_probability: DimensionScore
    sound_trend_timing: DimensionScore
    search_keyword_relevance: DimensionScore
    early_engagement_velocity: DimensionScore
    content_niche_fit: DimensionScore

    retention_drop_zones: list[RetentionDropZone]
    predicted_reach_range: str
    suggested_script_variant: Optional[str] = None

    debug_trace: list[str] = []



class AgentSkillScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    reason: str
    suggestions: list[str] = []


class AgentResult(BaseModel):
    name: str
    score: int = Field(..., ge=0, le=100)
    summary: str
    reason: str
    actionable_tips: list[str]
    skills: dict[str, AgentSkillScore] = {}
    extra: dict[str, Any] = {}
