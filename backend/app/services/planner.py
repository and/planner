"""
This is the core "AI engineering" part of the project.

Key concepts practiced here:
- Structured output via forced tool-use (so we always get valid JSON back,
  not free text we have to hope parses correctly)
- System prompt design encoding the *reasoning* we want (pacing, variety,
  burnout-avoidance) rather than just "make a schedule"
- Separating the LLM call from the data model (app/models/plan.py) so the
  eval step (later phase) can validate against the same schema
"""
import json
from anthropic import Anthropic

from app.config import get_settings
from app.models.plan import WeeklyPlan, PlanRequest

MODEL = "claude-sonnet-5"

PLAN_TOOL = {
    "name": "generate_weekly_plan",
    "description": "Return a structured, paced weekly plan across the user's interests.",
    "input_schema": {
        "type": "object",
        "properties": {
            "week_summary": {"type": "string"},
            "blocks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "day": {"type": "string"},
                        "time_range": {"type": "string"},
                        "activity": {"type": "string"},
                        "interest_area": {"type": "string"},
                        "intensity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "rationale": {"type": "string"},
                    },
                    "required": ["day", "time_range", "activity", "interest_area", "intensity", "rationale"],
                },
            },
            "burnout_risk_notes": {"type": "string"},
        },
        "required": ["week_summary", "blocks", "burnout_risk_notes"],
    },
}

SYSTEM_PROMPT = """You are a planning assistant that helps people with multiple interests \
build a sustainable weekly schedule WITHOUT burning out.

Core principles you must apply:
1. Variety across days — never stack multiple high-intensity activities back to back.
2. Respect the stated weekly time budget; do not overcommit.
3. Explicitly build in rest / buffer time, especially after high-intensity blocks.
4. If past_week_feedback indicates burnout or fatigue, actively reduce load or intensity \
this week and say so in burnout_risk_notes.
5. Every block must map to one of the user's stated interests — do not invent new ones.
6. Be realistic: use existing_commitments to avoid double-booking.

Always respond by calling the generate_weekly_plan tool. Do not respond in plain text.
"""


def _build_user_message(req: PlanRequest) -> str:
    return f"""
Interests: {", ".join(req.interests)}
Weekly time budget: {req.weekly_time_budget_hours} hours
Energy notes: {req.energy_notes or "none provided"}
Existing commitments: {", ".join(req.existing_commitments) or "none"}
Feedback from last week: {req.past_week_feedback or "none (first week)"}

Generate a paced weekly plan.
""".strip()


def generate_plan(req: PlanRequest) -> WeeklyPlan:
    settings = get_settings()
    client = Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[PLAN_TOOL],
        tool_choice={"type": "tool", "name": "generate_weekly_plan"},
        messages=[{"role": "user", "content": _build_user_message(req)}],
    )

    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    return WeeklyPlan(**tool_use_block.input)
