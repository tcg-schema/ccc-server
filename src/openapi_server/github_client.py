"""GitHub OAuth token-exchange relay.

This service exists almost entirely as a CORS shim: GitHub's OAuth token
endpoint does not send CORS headers, so a browser SPA cannot exchange an
authorization code directly. The browser runs the Authorization-Code + PKCE
flow itself (redirect to GitHub, receive ?code), then asks this relay to swap
the code for a token. The relay injects the client secret server-side — GitHub
still requires it even with PKCE — so the secret never reaches the browser. No
tokens are stored here.
"""

import os
from typing import Optional

import httpx

_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"

# OAuth App credentials. The client id is public (embedded in the SPA bundle);
# the secret stays here. GitHub requires the secret in the token exchange even
# when PKCE is used.
CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "")


async def exchange_code(
    code: str,
    redirect_uri: Optional[str] = None,
    code_verifier: Optional[str] = None,
    client_id: Optional[str] = None,
) -> dict:
    """Exchange an authorization code for an access token.

    Returns GitHub's raw JSON — either a token payload (``access_token``,
    ``token_type``, ``scope``) or an error payload (``error``,
    ``error_description``).
    """
    payload = {
        "client_id": client_id or CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
    }
    if redirect_uri:
        payload["redirect_uri"] = redirect_uri
    if code_verifier:
        payload["code_verifier"] = code_verifier

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            _ACCESS_TOKEN_URL,
            data=payload,
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()
