"""
Thin wrapper around the Todoist REST API (v2).
Docs: https://developer.todoist.com/rest/v2/
"""
import httpx
from app.config import get_settings

BASE_URL = "https://api.todoist.com/rest/v2"


def _headers() -> dict:
    settings = get_settings()
    return {"Authorization": f"Bearer {settings.todoist_api_token}"}


async def get_projects() -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/projects", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def get_active_tasks() -> list[dict]:
    """
    Returns all active (incomplete) tasks across all projects.
    Each task looks roughly like:
    {
        "id": "...", "content": "...", "project_id": "...",
        "due": {"date": "2026-07-05", ...} | None,
        "priority": 1-4, "labels": [...]
    }
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/tasks", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def create_task(content: str, due_string: str | None = None, project_id: str | None = None) -> dict:
    """
    Used later to write a generated plan back into Todoist as tasks.
    due_string supports natural language, e.g. "today at 6pm".
    """
    payload = {"content": content}
    if due_string:
        payload["due_string"] = due_string
    if project_id:
        payload["project_id"] = project_id

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BASE_URL}/tasks", headers=_headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
