from fastapi import APIRouter, HTTPException

from app.models.plan import PlanRequest, WeeklyPlan
from app.services import todoist, calendar as gcal
from app.services.planner import generate_plan

router = APIRouter(prefix="/api", tags=["plan"])


@router.get("/todoist/tasks")
async def list_todoist_tasks():
    return await todoist.get_active_tasks()


@router.get("/calendar/events")
async def list_calendar_events(days_ahead: int = 7):
    try:
        return await gcal.get_events(days_ahead=days_ahead)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/plan", response_model=WeeklyPlan)
async def create_plan(req: PlanRequest):
    """
    Core endpoint: takes interests/budget/feedback, returns a structured
    weekly plan. Doesn't touch Todoist/Calendar directly yet — that's the
    next step once you're comfortable with this loop.
    """
    return generate_plan(req)


@router.post("/plan/push-to-todoist")
async def push_plan_to_todoist(plan: WeeklyPlan):
    """
    Writes each plan block as a Todoist task with a natural-language due date.
    """
    created = []
    for block in plan.blocks:
        content = f"[{block.interest_area}] {block.activity} ({block.time_range})"
        due_string = f"{block.day} at {block.time_range.split('-')[0]}"
        task = await todoist.create_task(content=content, due_string=due_string)
        created.append(task)
    return {"created_count": len(created), "tasks": created}
