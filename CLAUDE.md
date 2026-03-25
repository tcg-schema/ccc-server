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

### Code generation pattern

The project follows an OpenAPI Generator convention:

- **`openapi.yaml`** — source of truth for the API contract. Regenerate with OpenAPI Generator when the spec changes.
- **`src/openapi_server/apis/*_api.py`** — generated FastAPI router files. Route handlers delegate to `Base*Api.subclasses[0]()`. **Do not implement logic here.**
- **`src/openapi_server/apis/*_api_base.py`** — generated abstract base classes with method stubs. **Do not implement logic here.**
- **`src/openapi_server/models/`** — generated Pydantic models. **Do not edit by hand.**
- **`src/openapi_server/impl/`** — **the only place to write business logic.** Create subclasses of the base API classes here. They are auto-discovered at startup via `pkgutil.iter_modules`.
- **`src/openapi_server/security_api.py`** — `get_token_sessionAuth` stub; implement session token validation here.

### API surface

Three routers, all prefixed relative to `/api` on the frontend:

| Router | Endpoints |
|---|---|
| Auth | `GET /auth/github` · `GET /auth/github/callback` · `GET /auth/me` · `POST /auth/logout` · `GET /auth/installations` |
| Projects | `POST /projects/{projectId}/save` · `GET /projects/{projectId}/load` · `POST /projects/{projectId}/export` |
| Repos | `GET /repos` |

All endpoints except the auth initiation require a Bearer session token (`Authorization: Bearer <token>`), validated by `get_token_sessionAuth`.

### Key behaviors (per openapi.yaml)

- **Save project**: commits `template.json`, `data.csv`, HTML cards, and JSON-LD (when TCG annotations present) to `cardforge/{projectName}/` in the target GitHub repo.
- **Load project**: reads `template.json` + `data.csv` from the repo and reconstructs a `CardProject`.
- **Export project**: returns a ZIP of the same artifacts without committing to GitHub.

### Tests

Test files in `tests/` are generated scaffolding — all actual assertions are commented out. Implement real tests by filling in the request/assertion blocks. The `client` fixture (from `conftest.py`) wraps the FastAPI app with `TestClient`.
