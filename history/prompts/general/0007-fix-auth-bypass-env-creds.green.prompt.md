---
id: 7
title: fix-auth-bypass-env-creds
stage: green
date: 2026-06-05
surface: agent
model: claude-opus-4-8[1m]
feature: none
branch: feature/psx-skills-architecture
user: architect
command: "as per last phr we have been build something please check and evaluate it first -> what should be next?"
labels: [security, auth, fastapi, bypass, dotenv, gitignore, housekeeping]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/auth.py
  - backend/main.py
  - backend/routers/market.py
  - backend/routers/journal.py
  - backend/routers/macro.py
  - backend/routers/pipeline.py
  - backend/requirements.txt
  - .gitignore (new)
  - .env.example (new)
  - .env (new, gitignored)
  - frontend/src/components/TradeJournal.tsx
tests:
  - "Auth bypass closed: garbage Authorization header now 401 on all 4 routers (was 200)"
  - "No-header 401, valid creds 200 on journal/market/macro/pipeline"
  - "Env override: AUTH_PASS=changed999 -> old creds 401, new creds 200"
  - "Backend imports clean (17 routes, no circular import)"
  - "Frontend tsc --noEmit exit 0"
  - "git ls-files has no __pycache__/*.pyc/*.db after untracking"
---

## Prompt

as per last phr we have been build something please check and evaluate it first
[then] what should be next?

## Response snapshot

Evaluated the uncommitted full-stack PSX app (FastAPI + React) built since commit
c556862. Verified backend imports, frontend typecheck, auth flow, and short-sell
P&L math — all functionally working. Found a real authentication bypass: the
global `auth_middleware` in main.py only checked that an `Authorization` header
existed, never validated it, and none of the 11 router endpoints carried
`Depends(require_auth)`. Proved it live — `Authorization: Basic garbage` returned
200 on `/api/journal/trades`.

Fixed per approved plan:
- Moved `require_auth` into `backend/auth.py` (avoids circular import) and added
  `dependencies=[Depends(require_auth)]` to all 4 routers (market, journal,
  macro, pipeline). Deleted the broken middleware from main.py.
- Credentials now read from `.env` via python-dotenv with admin/psx2026 defaults;
  added `.env.example` (committed) and `.env` (gitignored).
- Added root `.gitignore`; untracked `__pycache__/*.pyc` and `data/psx.db`.
- Removed dead `handleSymbolChange` in TradeJournal.tsx.

## Outcome

- ✅ Impact: Auth bypass closed across all routers; credentials externalized to .env; repo no longer tracks build artifacts/DB.
- 🧪 Tests: All smoke tests pass — garbage/no-header → 401, valid creds → 200 on every router; env override honoured; backend imports clean; frontend tsc exit 0.
- 📁 Files: 6 backend files, 1 frontend file, 3 new config files (.gitignore, .env, .env.example).
- 🔁 Next prompts: (1) Surface buy/sell signals on the frontend — analysis is computed but not shown. (2) Deploy backend+frontend to a public platform for any-device testing.
- 🧠 Reflection: The middleware was security theatre — present but ineffective. Router-level dependencies are the idiomatic, testable fix. Always assert the negative case (bad creds → 401), not just the positive.

## Evaluation notes (flywheel)

- Failure modes observed: Header-exists check masquerading as auth; require_auth originally in main.py would have caused circular import if imported by routers.
- Graders run and results (PASS/FAIL): PASS — bypass closed, env override works, builds clean.
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Wire signal/decision data into MarketGrid so buy/sell is visible; then containerize for deploy.
