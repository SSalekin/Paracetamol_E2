from typing import List

from pydantic import BaseModel, Field


class SkillResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    evidence: List[str] = Field(default_factory=list)
    actionable_fix: str
    warnings: List[str] = Field(default_factory=list)
