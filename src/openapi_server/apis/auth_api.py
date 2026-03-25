# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.auth_api_base import BaseAuthApi
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
from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.auth_session import AuthSession
from openapi_server.models.auth_user import AuthUser
from openapi_server.models.initiate_git_hub_auth200_response import InitiateGitHubAuth200Response
from openapi_server.models.installation import Installation
from openapi_server.security_api import get_token_sessionAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/auth/github",
    responses={
        200: {"model": InitiateGitHubAuth200Response, "description": "Authorization URL"},
    },
    tags=["Auth"],
    summary="Initiate GitHub App OAuth flow",
    response_model_by_alias=True,
)
async def initiate_git_hub_auth(
    return_to: Annotated[Optional[StrictStr], Field(description="URL to redirect back to after auth completes")] = Query(None, description="URL to redirect back to after auth completes", alias="return_to"),
) -> InitiateGitHubAuth200Response:
    """Returns a redirect URL to GitHub&#39;s authorization page. The frontend should redirect the user to this URL. The state parameter is generated server-side for CSRF protection. """
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().initiate_git_hub_auth(return_to)


@router.get(
    "/auth/github/callback",
    responses={
        200: {"model": AuthSession, "description": "Authentication successful, returns session"},
        400: {"description": "Invalid or expired code/state"},
        403: {"description": "User denied authorization"},
    },
    tags=["Auth"],
    summary="Handle GitHub OAuth callback",
    response_model_by_alias=True,
)
async def handle_git_hub_callback(
    code: Annotated[StrictStr, Field(description="Authorization code from GitHub")] = Query(None, description="Authorization code from GitHub", alias="code"),
    state: Annotated[StrictStr, Field(description="CSRF state token for validation")] = Query(None, description="CSRF state token for validation", alias="state"),
) -> AuthSession:
    """Receives the authorization code from GitHub after user approves. Exchanges it for an access token via the GitHub App. Creates or updates the user session and returns a session token. """
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().handle_git_hub_callback(code, state)


@router.get(
    "/auth/me",
    responses={
        200: {"model": AuthUser, "description": "Authenticated user"},
        401: {"description": "Not authenticated or session expired"},
    },
    tags=["Auth"],
    summary="Get current authenticated user",
    response_model_by_alias=True,
)
async def get_me(
    token_sessionAuth: TokenModel = Security(
        get_token_sessionAuth
    ),
) -> AuthUser:
    """Returns the currently authenticated user based on the session token. The backend resolves the GitHub identity from the stored access token. """
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().get_me()


@router.post(
    "/auth/logout",
    responses={
        204: {"description": "Logged out successfully"},
        401: {"description": "Not authenticated"},
    },
    tags=["Auth"],
    summary="Log out and destroy session",
    response_model_by_alias=True,
)
async def logout(
    token_sessionAuth: TokenModel = Security(
        get_token_sessionAuth
    ),
) -> None:
    """Invalidates the current session token and revokes the GitHub installation token if applicable. """
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().logout()


@router.get(
    "/auth/installations",
    responses={
        200: {"model": List[Installation], "description": "List of installations"},
        401: {"description": "Not authenticated"},
    },
    tags=["Auth"],
    summary="List GitHub App installations for the user",
    response_model_by_alias=True,
)
async def list_installations(
    token_sessionAuth: TokenModel = Security(
        get_token_sessionAuth
    ),
) -> List[Installation]:
    """Returns the GitHub App installations accessible to the authenticated user. Used to determine which organizations/accounts have the app installed. """
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().list_installations()
