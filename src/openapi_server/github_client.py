"""GitHub REST API helper — OAuth token exchange and repo/content operations."""

import base64
import os
from typing import Optional

import httpx

_API = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"
_API_VERSION = "2022-11-28"


def _h(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": _ACCEPT,
        "X-GitHub-Api-Version": _API_VERSION,
    }


async def exchange_code_for_token(code: str) -> str:
    client_id = os.environ.get("GITHUB_CLIENT_ID", "")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET", "")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={"client_id": client_id, "client_secret": client_secret, "code": code},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    if "error" in data:
        raise ValueError(data.get("error_description", data["error"]))
    return data["access_token"]


async def get_user(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_API}/user", headers=_h(access_token), timeout=10)
        resp.raise_for_status()
    return resp.json()


async def get_installations(access_token: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_API}/user/installations", headers=_h(access_token), timeout=10
        )
        resp.raise_for_status()
    return resp.json().get("installations", [])


async def get_repos(
    access_token: str,
    sort: str = "updated",
    per_page: int = 30,
) -> list[dict]:
    params = {"sort": sort, "per_page": min(per_page, 100), "visibility": "all"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_API}/user/repos", headers=_h(access_token), params=params, timeout=10
        )
        resp.raise_for_status()
    return [r for r in resp.json() if r.get("permissions", {}).get("push")]


async def get_file(
    access_token: str, repo: str, path: str
) -> Optional[tuple[bytes, str]]:
    """Returns (content_bytes, sha) or None if not found."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_API}/repos/{repo}/contents/{path}", headers=_h(access_token), timeout=15
        )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"].replace("\n", ""))
    return content, data["sha"]


async def commit_files(
    access_token: str,
    repo: str,
    branch: Optional[str],
    files: dict[str, bytes],
    message: str,
) -> str:
    """Commit multiple files atomically using the Git Data API. Returns new commit SHA."""
    hdrs = _h(access_token)

    async with httpx.AsyncClient(timeout=30) as client:
        # Resolve branch to default if not specified
        if not branch:
            r = await client.get(f"{_API}/repos/{repo}", headers=hdrs)
            r.raise_for_status()
            branch = r.json()["default_branch"]

        # Current HEAD commit on branch
        r = await client.get(f"{_API}/repos/{repo}/git/ref/heads/{branch}", headers=hdrs)
        r.raise_for_status()
        base_commit_sha = r.json()["object"]["sha"]

        # Tree SHA of that commit
        r = await client.get(
            f"{_API}/repos/{repo}/git/commits/{base_commit_sha}", headers=hdrs
        )
        r.raise_for_status()
        base_tree_sha = r.json()["tree"]["sha"]

        # Create a blob for each file
        tree_entries = []
        for path, content in files.items():
            r = await client.post(
                f"{_API}/repos/{repo}/git/blobs",
                headers=hdrs,
                json={"content": base64.b64encode(content).decode(), "encoding": "base64"},
            )
            r.raise_for_status()
            tree_entries.append(
                {"path": path, "mode": "100644", "type": "blob", "sha": r.json()["sha"]}
            )

        # Create new tree
        r = await client.post(
            f"{_API}/repos/{repo}/git/trees",
            headers=hdrs,
            json={"base_tree": base_tree_sha, "tree": tree_entries},
        )
        r.raise_for_status()
        new_tree_sha = r.json()["sha"]

        # Create commit
        r = await client.post(
            f"{_API}/repos/{repo}/git/commits",
            headers=hdrs,
            json={"message": message, "tree": new_tree_sha, "parents": [base_commit_sha]},
        )
        r.raise_for_status()
        new_commit_sha = r.json()["sha"]

        # Advance branch ref
        r = await client.patch(
            f"{_API}/repos/{repo}/git/refs/heads/{branch}",
            headers=hdrs,
            json={"sha": new_commit_sha},
        )
        r.raise_for_status()

    return new_commit_sha
