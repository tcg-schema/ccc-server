# coding: utf-8
"""CardForge render & auth proxy — a stateless FastAPI service.

The frontend stores card projects directly in the user's GitHub repos and
talks to ``api.github.com`` with the user's own token. This service only
provides the two things a browser cannot do on its own:

1. GitHub OAuth token exchange — the SPA runs the Authorization-Code + PKCE
   flow itself, then posts the code here to be swapped for a token (GitHub's
   token endpoint lacks CORS and still requires the client secret).
2. Optional server-side PDF rendering via WeasyPrint ("remote" render).

There is no database and no session state.
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from openapi_server import github_client

app = FastAPI(
    title="CardForge Proxy",
    description=(
        "Stateless helper for CardForge: GitHub OAuth token exchange (CORS shim) "
        "and optional remote PDF rendering. All persistence lives in the user's "
        "own GitHub repos."
    ),
    version="4.0.0",
)

# CORS — the SPA calls this from another origin (Netlify). Comma-separated list,
# or "*" for local dev.
_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz", include_in_schema=False)
async def healthz():
    return {
        "ok": True,
        "client_id_configured": bool(github_client.CLIENT_ID),
        "client_secret_configured": bool(github_client.CLIENT_SECRET),
    }


# ── GitHub OAuth token exchange (PKCE) ───────────────────────────────────────


@app.post("/auth/github/exchange")
async def github_exchange(body: dict):
    """Exchange an OAuth authorization code for an access token.

    The browser runs the Authorization-Code + PKCE flow and posts
    ``{ client_id, code, redirect_uri, code_verifier }`` here. We inject the
    client secret server-side (GitHub requires it even with PKCE) and return
    GitHub's JSON verbatim. The token is never stored.
    """
    body = body or {}
    code = body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code'")
    try:
        data = await github_client.exchange_code(
            code=code,
            redirect_uri=body.get("redirect_uri"),
            code_verifier=body.get("code_verifier"),
            client_id=body.get("client_id"),
        )
    except Exception as e:  # noqa: BLE001 — surface upstream failure to client
        raise HTTPException(status_code=502, detail=f"GitHub token exchange failed: {e}")
    return data


# ── Remote PDF render ────────────────────────────────────────────────────────


@app.post("/render/pdf")
async def render_pdf(body: dict):
    """Render a CardProject payload to a PDF via WeasyPrint (remote render).

    Requires WeasyPrint + its native libraries (Pango/Cairo). On hosts without
    them (e.g. Vercel's serverless runtime) this returns 501 — the frontend
    falls back to its built-in local print-to-PDF.
    """
    from openapi_server.card_renderer import project_to_pdf
    from openapi_server.models.card_project import CardProject

    project_data = (body or {}).get("project")
    if not project_data:
        raise HTTPException(status_code=400, detail="Missing 'project' in request body")

    project = CardProject.from_dict(project_data)
    try:
        # WeasyPrint is imported lazily inside project_to_pdf, so a missing
        # package (ImportError) or missing native lib (OSError) surfaces here.
        pdf_bytes = project_to_pdf(project)
    except (ImportError, OSError):
        raise HTTPException(
            status_code=501,
            detail=(
                "Remote PDF rendering is not available on this deployment "
                "(WeasyPrint/system libraries missing). Use the app's local PDF "
                "export, or run the render service on a container host."
            ),
        )
    filename = project.name.replace(" ", "_") + ".pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
