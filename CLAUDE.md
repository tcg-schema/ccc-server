# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the server locally
PYTHONPATH=src uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080

# Run tests
PYTHONPATH=src pytest tests

# Run a single test file
PYTHONPATH=src pytest tests/test_auth_api.py

# Docker
docker compose up --build
```

Formatting tools configured: `black` (line length 88) and `isort` (black-compatible profile).

Interactive API docs available at `http://localhost:8080/docs/` when running.

## Architecture

This is the **CardForge backend** — a FastAPI server generated from `openapi.yaml` using OpenAPI Generator (Python FastAPI codegen). It handles GitHub App OAuth and GitHub repo persistence for the card-canvas-creator frontend.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql://localhost/cardforge` | PostgreSQL connection string |
| `GITHUB_CLIENT_ID` | — | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | — | GitHub OAuth App client secret |
| `GITHUB_REDIRECT_URI` | — | OAuth callback URI (registered on GitHub App) |
| `SESSION_EXPIRY_HOURS` | `24` | How long session tokens remain valid |
| `ADMIN_TOKEN` | — | Bearer token for the `/admin` stats page |

### Code generation pattern

The project follows an OpenAPI Generator convention:

- **`openapi.yaml`** — source of truth for the API contract. Regenerate with OpenAPI Generator when the spec changes.
- **`src/openapi_server/apis/*_api.py`** — generated FastAPI router files. Route handlers delegate to `Base*Api.subclasses[0]()`. **Do not implement logic here.**
- **`src/openapi_server/apis/*_api_base.py`** — generated abstract base classes with method stubs. **Do not implement logic here.**
- **`src/openapi_server/models/`** — generated Pydantic models. **Do not edit by hand.**
- **`src/openapi_server/impl/`** — **the only place to write business logic.** Subclasses of the base classes are auto-discovered at startup via `pkgutil.iter_modules`.
- **`src/openapi_server/security_api.py`** — validates Bearer tokens against the DB; stores the session dict in a `ContextVar` (`current_session`) for impl methods to read.

### Database (Tortoise ORM + PostgreSQL)

Models are defined in `src/openapi_server/db.py` and registered in `main.py` via `register_tortoise`. Schemas are auto-generated on startup (`generate_schemas=True`).

| Table | Purpose |
|---|---|
| `sessions` | Active user sessions (session_token → GitHub access token + user info) |
| `oauth_states` | Short-lived CSRF state tokens for the OAuth flow (10-min TTL enforced at read) |
| `project_saves` | Audit log of every save-to-GitHub operation |

Use `tortoise-orm[asyncpg]` — never raw `asyncpg` directly.

### API surface

| Router | Endpoints |
|---|---|
| Auth | `GET /auth/github` · `GET /auth/github/callback` · `GET /auth/me` · `POST /auth/logout` · `GET /auth/installations` |
| Projects | `POST /projects/{id}/save` · `GET /projects/{id}/load` · `POST /projects/{id}/export` (ZIP) |
| Repos | `GET /repos` |
| Extra | `POST /projects/{id}/export/pdf` (WeasyPrint, outside spec) · `GET /admin?token=` (stats HTML) |

All spec endpoints except `GET /auth/github` and `GET /auth/github/callback` require `Authorization: Bearer <session_token>`.

### Key implementation notes

- **Save project**: commits files atomically to `cardforge/{projectId}/` in the target GitHub repo using the Git Data API (create blobs → tree → commit → update ref). Saves `project.json`, per-sheet `template.json`/`data.csv`/`data.json`/`card_N.html`, and optionally `cards.jsonld` when TCG annotations are present.
- **Load project**: reads `cardforge/{projectId}/project.json` from the repo.
- **PDF export**: `card_renderer.project_to_pdf()` generates HTML and converts it with WeasyPrint. WeasyPrint requires system libraries (`libpango`, `libcairo`, etc.) — already satisfied in the Docker image.
- **Session flow**: `get_token_sessionAuth` (in `security_api.py`) looks up the token in the DB and populates the `current_session` ContextVar. Impl methods call `current_session.get()` to access `github_access_token`, `user_login`, etc.

### Tests

Test files in `tests/` are generated scaffolding — all actual assertions are commented out. Implement real tests by filling in the request/assertion blocks. The `client` fixture (from `conftest.py`) wraps the FastAPI app with `TestClient`.
