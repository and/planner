from fastapi import APIRouter, HTTPException, Response

from app.models.plan import PlanRequest, WeeklyPlan
from app.services import storage, todoist, calendar as gcal
from app.services.planner import generate_plan
from app.services.wallpaper import render_weekly_plan_png

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
    plan = generate_plan(req)
    storage.save_latest_plan(plan)
    return plan


@router.get("/plan/wallpaper")
async def get_plan_wallpaper():
    """
    Renders the most recently generated plan as a bird's-eye PNG, sized for
    a phone lock screen. Meant to be polled by a device-side automation
    (e.g. a Tasker HTTP Request + Set Wallpaper profile) rather than by
    the frontend.
    """
    plan = storage.load_latest_plan()
    if plan is None:
        raise HTTPException(status_code=404, detail="No plan generated yet. Call POST /api/plan first.")
    png_bytes = render_weekly_plan_png(plan)
    return Response(content=png_bytes, media_type="image/png")


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
