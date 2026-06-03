# CardForge proxy

A small **stateless** FastAPI service. CardForge stores all card projects
directly in the user's own GitHub repositories; the browser talks to
`api.github.com` with the user's token. This service only provides the two
things a browser can't do on its own:

1. **GitHub OAuth token exchange** — the browser runs the Authorization-Code +
   PKCE flow itself, then posts the code to `POST /auth/github/exchange`. GitHub's
   token endpoint has no CORS and still requires the client secret even with
   PKCE, so the secret is injected here server-side (never in the browser).
2. **Remote PDF rendering** — `POST /render/pdf` renders a `CardProject`
   payload to a PDF with WeasyPrint. (The frontend can also render locally.)

There is **no database**.

## Setup

Create a GitHub **OAuth App** (https://github.com/settings/developers → New
OAuth App). Set the **Authorization callback URL** to `<frontend-origin>/auth/callback`
(e.g. `http://localhost:8080/auth/callback` for local dev). Copy `.env.example`
to `.env` and set `GITHUB_CLIENT_ID` + `GITHUB_CLIENT_SECRET`.

## Run

```bash
pip3 install -r requirements.txt
GITHUB_CLIENT_ID=... GITHUB_CLIENT_SECRET=... PYTHONPATH=src uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080
```

Open `http://localhost:8080/docs/` for the interactive API docs.

## Docker

```bash
GITHUB_CLIENT_ID=... GITHUB_CLIENT_SECRET=... docker compose up --build
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/healthz` | Liveness + whether the client id/secret are configured |
| POST | `/auth/github/exchange` | Swap an OAuth code (+ PKCE verifier) for a token |
| POST | `/render/pdf` | Render a `CardProject` to PDF (WeasyPrint) |
