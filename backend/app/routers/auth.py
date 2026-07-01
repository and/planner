from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.services.calendar import build_auth_flow, save_credentials
from app.config import get_settings

router = APIRouter(prefix="/auth/google", tags=["auth"])


@router.get("/login")
def login():
    """
    Visit this endpoint in your browser once. It redirects you to Google's
    consent screen. After approving, Google redirects back to /callback.
    """
    flow = build_auth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
def callback(code: str):
    flow = build_auth_flow()
    flow.fetch_token(code=code)
    save_credentials(flow.credentials)

    settings = get_settings()
    return RedirectResponse(f"{settings.frontend_origin}/?calendar_connected=true")
