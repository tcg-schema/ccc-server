# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.repos_api_base import BaseReposApi
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
from pydantic import Field, StrictInt, StrictStr, field_validator
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.repo_summary import RepoSummary
from openapi_server.security_api import get_token_sessionAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/repos",
    responses={
        200: {"model": List[RepoSummary], "description": "List of repositories"},
        401: {"description": "Not authenticated"},
    },
    tags=["Repos"],
    summary="List repositories the user can push to",
    response_model_by_alias=True,
)
async def list_repos(
    installation_id: Annotated[Optional[StrictInt], Field(description="Filter by specific installation")] = Query(None, description="Filter by specific installation", alias="installation_id"),
    sort: Optional[StrictStr] = Query(updated, description="", alias="sort"),
    per_page: Optional[Annotated[int, Field(le=100, strict=True)]] = Query(30, description="", alias="per_page", le=100),
    token_sessionAuth: TokenModel = Security(
        get_token_sessionAuth
    ),
) -> List[RepoSummary]:
    """Returns repositories accessible via the GitHub App installation. Filtered to repos where the user has push access. """
    if not BaseReposApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseReposApi.subclasses[0]().list_repos(installation_id, sort, per_page)
