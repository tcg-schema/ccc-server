# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.auth_session import AuthSession
from openapi_server.models.auth_user import AuthUser
from openapi_server.models.initiate_git_hub_auth200_response import InitiateGitHubAuth200Response
from openapi_server.models.installation import Installation
from openapi_server.security_api import get_token_sessionAuth

class BaseAuthApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuthApi.subclasses = BaseAuthApi.subclasses + (cls,)
    async def initiate_git_hub_auth(
        self,
        return_to: Annotated[Optional[StrictStr], Field(description="URL to redirect back to after auth completes")],
    ) -> InitiateGitHubAuth200Response:
        """Returns a redirect URL to GitHub&#39;s authorization page. The frontend should redirect the user to this URL. The state parameter is generated server-side for CSRF protection. """
        ...


    async def handle_git_hub_callback(
        self,
        code: Annotated[StrictStr, Field(description="Authorization code from GitHub")],
        state: Annotated[StrictStr, Field(description="CSRF state token for validation")],
    ) -> AuthSession:
        """Receives the authorization code from GitHub after user approves. Exchanges it for an access token via the GitHub App. Creates or updates the user session and returns a session token. """
        ...


    async def get_me(
        self,
    ) -> AuthUser:
        """Returns the currently authenticated user based on the session token. The backend resolves the GitHub identity from the stored access token. """
        ...


    async def logout(
        self,
    ) -> None:
        """Invalidates the current session token and revokes the GitHub installation token if applicable. """
        ...


    async def list_installations(
        self,
    ) -> List[Installation]:
        """Returns the GitHub App installations accessible to the authenticated user. Used to determine which organizations/accounts have the app installed. """
        ...
