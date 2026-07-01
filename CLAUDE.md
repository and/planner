# Day Planner AI — context for Claude Code

## What this project is
A personal tool that generates a paced weekly plan across multiple interests
(e.g. guitar, working out, side project, reading) without burning the user
out. It's also a deliberate learning project: each feature maps to a specific
AI engineering concept the user is learning (see "Learning phases" below).

**When making changes, prefer explaining *which concept* a change relates to**
in commit messages or comments — that traceability is the point of this repo,
not just working code.

## Structure
```
backend/     FastAPI. All AI/LLM logic lives here.
  app/routers/    HTTP route handlers (auth.py, plan.py)
  app/services/   External integrations + core logic
    todoist.py      Todoist REST API (Bearer token auth)
    calendar.py     Google Calendar (OAuth2, token cached in token.json)
    planner.py      Core LLM call — Anthropic API, forced tool-use for
                     structured output. Model string, system prompt, and
                     the tool schema all live here.
  app/models/plan.py   Pydantic schema for the weekly plan (shared between
                        the LLM tool schema and API responses)
  main.py         FastAPI app entrypoint, CORS, router registration

frontend/    Next.js (App Router, TypeScript, Tailwind).
  app/page.tsx    Single page: form → POST /api/plan → render structured plan
```

## Running locally
Backend:
```bash
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000
```
Frontend:
```bash
cd frontend && npm run dev
```
Backend docs/interactive testing: http://localhost:8000/docs

## Conventions
- Backend: Python, FastAPI, Pydantic models for all request/response bodies.
  Async where the call is I/O (httpx, Google API), sync is fine for the
  Anthropic SDK call itself.
- Never hardcode secrets — everything sensitive goes through `.env`
  (see `.env.example` for required keys) or `token.json` (gitignored,
  created by the Google OAuth flow at runtime).
- LLM calls always use forced tool-use for structured output (see
  `planner.py`) rather than parsing free text — don't regress to prompting
  for "respond in JSON" as plain text.
- Frontend: keep it a thin client. Business logic (pacing rules, prompt
  design, schema validation) belongs in the backend, not in React state.

## Learning phases (current progress)
1. ✅ Foundations — basic API call, plain script
2. ✅ Structured output — JSON schema via tool-use, FastAPI + Next.js scaffold
3. ⬜ Reasoning & pacing — wire real Todoist tasks + Calendar events into the
   prompt (`planner._build_user_message`), add few-shot good/bad plan examples
4. ⬜ Memory — persist past plans + feedback (start with a flat JSON file)
5. ⬜ Evals — build a small eval set, try rule-based scoring then AI-as-judge
6. ⬜ Agents — let the tool check calendar availability and adjust itself
7. ⬜ Fine-tuning exploration (optional)
8. ⬜ Production polish — cost tracking, caching, guardrails

When picking up a task, check which phase it belongs to and read the
matching section in the root README.md for more detail before starting.

## Known gaps / intentionally not done yet
- Todoist tasks and Calendar events are fetched via API but NOT yet fed into
  the plan-generation prompt. That's the next real piece of work (Phase 3).
- No persistence layer yet — plans aren't saved anywhere. Needed before evals
  are possible (Phase 4 before Phase 5).
- No tests yet. Given this is a learning project, favor adding a couple of
  eval-style tests over unit tests when it's time (see Phase 5).
