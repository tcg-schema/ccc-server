# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.projects_api_base import BaseProjectsApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictBytes, StrictStr
from typing import Any, Tuple, Union
from typing_extensions import Annotated
from openapi_server.models.card_project import CardProject
from openapi_server.models.export_project_request import ExportProjectRequest
from openapi_server.models.save_project_request import SaveProjectRequest
from openapi_server.models.save_project_response import SaveProjectResponse
from openapi_server.security_api import get_token_sessionAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/projects/{projectId}/save",
    responses={
        200: {"model": SaveProjectResponse, "description": "Project saved successfully"},
        400: {"description": "Invalid project or missing template"},
        401: {"description": "Not authenticated"},
    },
    tags=["Projects"],
    summary="Save a CardForge project to a GitHub repo",
    response_model_by_alias=True,
)
async def save_project(
    projectId: StrictStr = Path(..., description=""),
    save_project_request: SaveProjectRequest = Body(None, description=""),
    token_sessionAuth: TokenModel = Security(
        get_token_sessionAuth
    ),
) -> SaveProjectResponse:
    """Receives the full project payload. The backend generates template.json, data.csv, card HTML files, and JSON-LD (if TCG annotations are present), then commits them to the specified GitHub repo under &#x60;cardforge/{projectName}/&#x60;. """
    if not BaseProjectsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProjectsApi.subclasses[0]().save_project(projectId, save_project_request)


@router.get(
    "/projects/{projectId}/load",
    responses={
        200: {"model": CardProject, "description": "Project loaded"},
        404: {"description": "Project not found in repo"},
    },
    tags=["Projects"],
    summary="Load a CardForge project from a GitHub repo",
    response_model_by_alias=True,
)
async def load_project(
    projectId: StrictStr = Path(..., description=""),
    repo: Annotated[StrictStr, Field(description="Full repo name (owner/repo)")] = Query(None, description="Full repo name (owner/repo)", alias="repo"),
    token_sessionAuth: TokenModel = Security(
        get_token_sessionAuth
    ),
) -> CardProject:
    """Reads template.json and data.csv from the repo and reconstructs the CardProject object. """
    if not BaseProjectsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProjectsApi.subclasses[0]().load_project(projectId, repo)


@router.post(
    "/projects/{projectId}/export",
    responses={
        200: {"model": file, "description": "Zip archive"},
    },
    tags=["Projects"],
    summary="Export rendered cards without saving to GitHub",
    response_model_by_alias=True,
)
async def export_project(
    projectId: StrictStr = Path(..., description=""),
    export_project_request: ExportProjectRequest = Body(None, description=""),
    token_sessionAuth: TokenModel = Security(
        get_token_sessionAuth
    ),
) -> file:
    """Returns a zip archive of generated HTML cards, JSON-LD, template.json, and data.csv — without committing to a repo. """
    if not BaseProjectsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseProjectsApi.subclasses[0]().export_project(projectId, export_project_request)
