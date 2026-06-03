# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the server locally (needs a GitHub OAuth App client id + secret)
GITHUB_CLIENT_ID=... GITHUB_CLIENT_SECRET=... PYTHONPATH=src uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080

# Docker
GITHUB_CLIENT_ID=... GITHUB_CLIENT_SECRET=... docker compose up --build
```

Formatting tools configured: `black` (line length 88) and `isort` (black-compatible profile).
Interactive API docs at `http://localhost:8080/docs/`.

## Architecture

This is the **CardForge proxy** — a **stateless** FastAPI service. CardForge is
"GitHub as backend": the frontend stores every card project directly in the
user's own GitHub repos (one private `cardforge-<slug>` repo per project, plus a
`cardforge-index` repo) and talks to `api.github.com` with the user's token.

This service exists only for the two things a browser can't do alone:

1. **GitHub OAuth token exchange** — the SPA runs the Authorization-Code + PKCE
   flow itself (redirect to GitHub → `?code`), then posts the code to
   `/auth/github/exchange`. GitHub's token endpoint has no CORS and still
   requires the client secret even with PKCE, so the secret is injected here.
2. **Remote PDF rendering** — WeasyPrint, for high-fidelity output. (The frontend
   also has a local, dependency-free print-to-PDF path.)

There is **no database, no session store, and no stored tokens.**

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `GITHUB_CLIENT_ID` | — | OAuth App client id (public; also embedded in the SPA). |
| `GITHUB_CLIENT_SECRET` | — | OAuth App secret. Required — GitHub needs it in the exchange even with PKCE. |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS allow-list (set to the frontend origin in prod). |

The OAuth App's **Authorization callback URL** must be `<frontend-origin>/auth/callback`.

### Modules (`src/openapi_server/`)

- **`main.py`** — the whole app: CORS, `/healthz`, `/auth/github/exchange`,
  `/render/pdf`. Routes are defined inline; there is no OpenAPI-generated router
  layer anymore.
- **`github_client.py`** — `exchange_code()`: swaps an OAuth code (+ PKCE
  verifier) for a token, injecting the client secret. A CORS shim; stores nothing.
- **`card_renderer.py`** — HTML/CSV/JSON-LD/ZIP/PDF helpers. Only
  `project_to_pdf()` is used by the service (for `/render/pdf`); the rest mirror
  the frontend's exporters and are kept for parity.
- **`models/`** — Pydantic models (`CardProject`, `CardTemplate`, …) consumed by
  `card_renderer`. Generated; do not edit by hand.

### Exchange contract

- `POST /auth/github/exchange` body `{ code, redirect_uri, code_verifier, client_id }`
  → GitHub's JSON verbatim: a token payload (`{ access_token, token_type, scope }`)
  or an error payload (`{ error, error_description }`).

### What was removed (v3 → v4)

PostgreSQL + Tortoise ORM, server-side OAuth web flow, sessions/oauth-state/save-log
tables, the `/admin` stats page, the `repos`/`projects` REST endpoints, and the
generated `apis/` + `impl/` router layer. All of that moved into the browser
(direct GitHub API) or was dropped.
