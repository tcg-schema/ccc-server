# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictInt, StrictStr, field_validator
from typing import Any, List, Optional
from typing_extensions import Annotated
from openapi_server.models.repo_summary import RepoSummary
from openapi_server.security_api import get_token_sessionAuth

class BaseReposApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseReposApi.subclasses = BaseReposApi.subclasses + (cls,)
    async def list_repos(
        self,
        installation_id: Annotated[Optional[StrictInt], Field(description="Filter by specific installation")],
        sort: Optional[StrictStr],
        per_page: Optional[Annotated[int, Field(le=100, strict=True)]],
    ) -> List[RepoSummary]:
        """Returns repositories accessible via the GitHub App installation. Filtered to repos where the user has push access. """
        ...
