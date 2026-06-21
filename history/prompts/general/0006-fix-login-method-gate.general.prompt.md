---
id: 6
title: fix-login-method-gate
stage: misc
date: 2026-05-31
surface: agent
model: deepseek-v4-flash-free
feature: none
branch: main
user: anonymous
command: i cant login with AUTH_USER = "admin" AUTH_PASS = "psx2026"
labels: [bug, login, auth, frontend, fetch]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/api/client.ts
tests: []
---

## Prompt

i cant login with AUTH_USER = "admin"
AUTH_PASS = "psx2026"

## Response snapshot

Diagnosed that backend and frontend were not running — started both (uvicorn on :8000, vite on :5173) — but login still failed. Found bug: `frontend/src/api/client.ts:42` call to `fetch()` for login omitted `method`, defaulting to GET, while the backend endpoint `@app.post("/api/auth/login")` only accepts POST, returning 405 Method Not Allowed. The catch block in App.tsx surfaced "Invalid username or password" regardless of actual error. Fixed by adding `method: 'POST'` to the fetch call.

## Outcome

- ✅ Impact: Login now works — frontend sends POST which backend accepts, returning 200 with `{"user":"admin","message":"Authenticated"}`.
- 🧪 Tests: Verified with curl to both :8000 (direct) and :5173 (via vite proxy) that POST succeeds and GET returns 405.
- 📁 Files: `frontend/src/api/client.ts` — one-line change
- 🔁 Next prompts: None
- 🧠 Reflection: The 405 was swallowed by a generic catch message. Two problems: the missing method, and the error masking. Consider surfacing the real HTTP error in the UI for future debugging.

## Evaluation notes (flywheel)

- Failure modes observed: Generic error message masked the real cause (405 vs 401).
- Graders run and results (PASS/FAIL): PASS — login works end-to-end
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Surface real HTTP status in frontend error messages
