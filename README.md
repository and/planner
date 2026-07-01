# Day Planner AI

A tool that plans your week across multiple interests without burning out —
built as a learning project pairing each feature with an AI engineering concept.

## Structure
```
backend/     FastAPI — all the AI logic lives here
frontend/    Next.js — the daily-use interface
```

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
- `ANTHROPIC_API_KEY` — from https://console.anthropic.com
- `TODOIST_API_TOKEN` — Todoist → Settings → Integrations → Developer → API token
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — create an OAuth 2.0 Client ID
  (type: Web application) at https://console.cloud.google.com/apis/credentials,
  after enabling the "Google Calendar API" for the project.
  Add `http://localhost:8000/auth/google/callback` as an authorized redirect URI.

Run it:
```bash
uvicorn main:app --reload --port 8000
```

Then, once, visit `http://localhost:8000/auth/google/login` in your browser to
connect your calendar (one-time consent flow; token is cached in `token.json`).

Docs / try endpoints interactively: `http://localhost:8000/docs`

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`. It talks to the backend at the URL set in
`.env.local` (`NEXT_PUBLIC_API_BASE`, defaults to `http://localhost:8000`).

## What's built so far (Phase 1-2)

- `POST /api/plan` — takes your interests, weekly time budget, energy notes,
  and optional feedback from last week, returns a **structured** weekly plan
  (not free text) using Anthropic's tool-use forced structured output.
- `GET /api/todoist/tasks` — pulls your current Todoist tasks (not yet wired
  into the plan prompt — that's a good next step).
- `GET /api/calendar/events` — pulls upcoming calendar events (also not yet
  wired into the prompt).
- `POST /api/plan/push-to-todoist` — writes a generated plan back into
  Todoist as tasks with due dates.

## Concepts practiced so far
- Structured output via forced tool-use (`app/services/planner.py`)
- System prompt design encoding actual reasoning (pacing, variety, burnout
  awareness) instead of a bare instruction
- Separating the LLM call, the data schema, and the API layer
- Real OAuth (Google) vs simple token auth (Todoist) — different auth
  patterns you'll hit constantly in real integrations

## Suggested next steps (Phase 3+)
1. Wire Todoist tasks + Calendar events into the `_build_user_message` prompt
   in `planner.py` so plans respect what's already committed.
2. Add few-shot examples of "good" vs "bad" plans to the system prompt.
3. Store generated plans + user feedback somewhere (start with a flat JSON
   file, no need for a database yet) — this becomes your eval dataset.
4. Build a small eval script: given a plan + feedback, score it (rule-based
   first, then try an AI-as-judge prompt) for variety/pacing/burnout risk.
