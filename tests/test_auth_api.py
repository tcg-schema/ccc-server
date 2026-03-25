# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictStr  # noqa: F401
from typing import Any, List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.auth_session import AuthSession  # noqa: F401
from openapi_server.models.auth_user import AuthUser  # noqa: F401
from openapi_server.models.initiate_git_hub_auth200_response import InitiateGitHubAuth200Response  # noqa: F401
from openapi_server.models.installation import Installation  # noqa: F401


def test_initiate_git_hub_auth(client: TestClient):
    """Test case for initiate_git_hub_auth

    Initiate GitHub App OAuth flow
    """
    params = [("return_to", 'return_to_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/auth/github",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_handle_git_hub_callback(client: TestClient):
    """Test case for handle_git_hub_callback

    Handle GitHub OAuth callback
    """
    params = [("code", 'code_example'),     ("state", 'state_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/auth/github/callback",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_me(client: TestClient):
    """Test case for get_me

    Get current authenticated user
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/auth/me",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_logout(client: TestClient):
    """Test case for logout

    Log out and destroy session
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/logout",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_list_installations(client: TestClient):
    """Test case for list_installations

    List GitHub App installations for the user
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/auth/installations",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

