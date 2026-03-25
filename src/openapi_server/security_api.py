# coding: utf-8

from contextvars import ContextVar
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from openapi_server.models.extra_models import TokenModel

bearer_auth = HTTPBearer()

# Populated by get_token_sessionAuth; read by impl methods.
current_session: ContextVar[dict] = ContextVar("current_session", default={})


async def get_token_sessionAuth(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_auth),
) -> TokenModel:
    from openapi_server.db import Session as DBSession  # avoid circular import at module load

    token = credentials.credentials
    session = await DBSession.filter(
        session_token=token,
        expires_at__gt=datetime.now(timezone.utc),
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    current_session.set(
        {
            "session_token": session.session_token,
            "github_access_token": session.github_access_token,
            "user_login": session.user_login,
            "user_name": session.user_name,
            "user_avatar_url": session.user_avatar_url,
        }
    )
    return TokenModel(sub=token)

