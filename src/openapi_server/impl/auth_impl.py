import os

from fastapi import HTTPException

from openapi_server.apis.auth_api_base import BaseAuthApi
from openapi_server.db import consume_oauth_state, create_oauth_state, create_session, delete_session
from openapi_server.github_client import exchange_code_for_token, get_installations, get_user
from openapi_server.models.auth_session import AuthSession
from openapi_server.models.auth_user import AuthUser
from openapi_server.models.initiate_git_hub_auth200_response import InitiateGitHubAuth200Response
from openapi_server.models.installation import Installation
from openapi_server.models.installation_account import InstallationAccount
from openapi_server.security_api import current_session

_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
_REDIRECT_URI = os.environ.get("GITHUB_REDIRECT_URI", "")


class AuthApiImpl(BaseAuthApi):
    async def initiate_git_hub_auth(self, return_to):
        state = await create_oauth_state(return_to)
        params = f"client_id={_CLIENT_ID}&state={state}&scope=repo,read:user"
        if _REDIRECT_URI:
            params += f"&redirect_uri={_REDIRECT_URI}"
        url = f"https://github.com/login/oauth/authorize?{params}"
        return InitiateGitHubAuth200Response(authorization_url=url)

    async def handle_git_hub_callback(self, code, state):
        return_to = await consume_oauth_state(state)
        if return_to is None:
            raise HTTPException(status_code=400, detail="Invalid or expired state")

        try:
            access_token = await exchange_code_for_token(code)
        except ValueError as exc:
            raise HTTPException(status_code=403, detail=str(exc))

        user_data = await get_user(access_token)
        session_token, expires_at = await create_session(
            github_access_token=access_token,
            user_login=user_data["login"],
            user_name=user_data.get("name"),
            user_avatar_url=user_data.get("avatar_url"),
        )
        user = AuthUser(
            login=user_data["login"],
            avatar_url=user_data.get("avatar_url"),
            name=user_data.get("name"),
        )
        return AuthSession(session_token=session_token, user=user, expires_at=expires_at)

    async def get_me(self):
        sess = current_session.get()
        return AuthUser(
            login=sess["user_login"],
            avatar_url=sess.get("user_avatar_url"),
            name=sess.get("user_name"),
        )

    async def logout(self):
        sess = current_session.get()
        await delete_session(sess["session_token"])

    async def list_installations(self):
        sess = current_session.get()
        raw = await get_installations(sess["github_access_token"])
        result = []
        for inst in raw:
            acc = inst.get("account", {})
            result.append(
                Installation(
                    id=inst.get("id"),
                    repository_selection=inst.get("repository_selection"),
                    permissions=inst.get("permissions"),
                    account=InstallationAccount(
                        login=acc.get("login"),
                        avatar_url=acc.get("avatar_url"),
                        type=acc.get("type"),
                    ),
                )
            )
        return result
