from pydantic import BaseModel, Field
from typing import Literal

Intensity = Literal["low", "medium", "high"]


class PlanBlock(BaseModel):
    day: str = Field(description="e.g. 'Monday'")
    time_range: str = Field(description="e.g. '7:00-8:00'")
    activity: str
    interest_area: str = Field(description="Which of the user's interests this maps to")
    intensity: Intensity
    rationale: str = Field(description="Why this is placed here (pacing/variety reasoning)")


class WeeklyPlan(BaseModel):
    week_summary: str
    blocks: list[PlanBlock]
    burnout_risk_notes: str = Field(
        description="Explicit reasoning about pacing/variety/rest across the week"
    )


class PlanRequest(BaseModel):
    interests: list[str]
    weekly_time_budget_hours: float
    energy_notes: str = ""
    existing_commitments: list[str] = []
    past_week_feedback: str = ""
