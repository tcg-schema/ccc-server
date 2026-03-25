# coding: utf-8

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.security import HTTPBearer
from tortoise.contrib.fastapi import register_tortoise

from openapi_server.admin import router as AdminRouter
from openapi_server.apis.auth_api import router as AuthApiRouter
from openapi_server.apis.projects_api import router as ProjectsApiRouter
from openapi_server.apis.repos_api import router as ReposApiRouter

_DB_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/cardforge")

# register_tortoise handles startup/teardown via the app lifespan
app = FastAPI(
    title="CardForge API",
    description=(
        "Backend API for CardForge. Authentication is handled via GitHub App OAuth flow "
        "(server-side). The backend manages GitHub tokens and interacts with GitHub on "
        "behalf of the user."
    ),
    version="3.0.0",
)

register_tortoise(
    app,
    db_url=_DB_URL,
    modules={"models": ["openapi_server.db"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.include_router(AuthApiRouter)
app.include_router(ProjectsApiRouter)
app.include_router(ReposApiRouter)
app.include_router(AdminRouter)


# ── Extra endpoint: PDF export (not in OpenAPI spec) ─────────────────────────

_bearer = HTTPBearer(auto_error=False)


@app.post("/projects/{projectId}/export/pdf", include_in_schema=False)
async def export_project_pdf(projectId: str, body: dict):
    """Generate a PDF from a CardProject payload via WeasyPrint."""
    from openapi_server.card_renderer import project_to_pdf
    from openapi_server.models.card_project import CardProject

    project_data = body.get("project")
    if not project_data:
        raise HTTPException(status_code=400, detail="Missing 'project' in request body")

    project = CardProject.from_dict(project_data)
    pdf_bytes = project_to_pdf(project)
    filename = project.name.replace(" ", "_") + ".pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
