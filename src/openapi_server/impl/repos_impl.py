from openapi_server.apis.repos_api_base import BaseReposApi
from openapi_server.github_client import get_repos
from openapi_server.models.repo_summary import RepoSummary
from openapi_server.security_api import current_session


class ReposApiImpl(BaseReposApi):
    async def list_repos(self, installation_id, sort, per_page):
        sess = current_session.get()
        repos = await get_repos(
            access_token=sess["github_access_token"],
            sort=sort or "updated",
            per_page=per_page or 30,
        )
        return [
            RepoSummary(
                full_name=r["full_name"],
                name=r["name"],
                owner=r["owner"]["login"],
                private=r["private"],
                default_branch=r.get("default_branch", "main"),
            )
            for r in repos
        ]
