"""
Google Calendar integration.

For a personal single-user tool, we do a one-time OAuth flow (via the
/auth/google routes) and cache the resulting token on disk in token.json.
Every subsequent request reuses/refreshes that token — no need to
re-authenticate each time.
"""
import json
import os
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.config import get_settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")


def build_auth_flow() -> Flow:
    settings = get_settings()
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = settings.google_redirect_uri
    return flow


def save_credentials(creds: Credentials) -> None:
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())


def load_credentials() -> Credentials | None:
    if not os.path.exists(TOKEN_PATH):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_credentials(creds)
    return creds


def _service():
    creds = load_credentials()
    if not creds:
        raise RuntimeError("Google Calendar not authorized yet. Visit /auth/google/login first.")
    return build("calendar", "v3", credentials=creds)


async def get_events(days_ahead: int = 7) -> list[dict]:
    service = _service()
    now = datetime.utcnow().isoformat() + "Z"
    later = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=later,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])


async def create_event(summary: str, start_iso: str, end_iso: str, description: str = "") -> dict:
    """
    Writes a generated plan block onto the calendar.
    start_iso/end_iso example: "2026-07-02T09:00:00-07:00"
    """
    service = _service()
    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_iso},
    }
    return service.events().insert(calendarId="primary", body=event_body).execute()
