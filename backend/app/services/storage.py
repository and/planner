"""Flat-file persistence for the most recently generated plan.

Minimal stand-in for Phase 4 (Memory) — just enough state so the wallpaper
endpoint has something to render without requiring the caller to resend the
whole plan on every request.
"""
import json
from pathlib import Path

from app.models.plan import WeeklyPlan

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_LATEST_PLAN_PATH = _DATA_DIR / "latest_plan.json"


def save_latest_plan(plan: WeeklyPlan) -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _LATEST_PLAN_PATH.write_text(plan.model_dump_json())


def load_latest_plan() -> WeeklyPlan | None:
    if not _LATEST_PLAN_PATH.exists():
        return None
    return WeeklyPlan.model_validate_json(_LATEST_PLAN_PATH.read_text())
