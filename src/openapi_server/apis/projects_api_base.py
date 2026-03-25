# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictBytes, StrictStr
from typing import Any, Tuple, Union
from typing_extensions import Annotated
from openapi_server.models.card_project import CardProject
from openapi_server.models.export_project_request import ExportProjectRequest
from openapi_server.models.save_project_request import SaveProjectRequest
from openapi_server.models.save_project_response import SaveProjectResponse
from openapi_server.security_api import get_token_sessionAuth

class BaseProjectsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseProjectsApi.subclasses = BaseProjectsApi.subclasses + (cls,)
    async def save_project(
        self,
        projectId: StrictStr,
        save_project_request: SaveProjectRequest,
    ) -> SaveProjectResponse:
        """Receives the full project payload. The backend generates template.json, data.csv, card HTML files, and JSON-LD (if TCG annotations are present), then commits them to the specified GitHub repo under &#x60;cardforge/{projectName}/&#x60;. """
        ...


    async def load_project(
        self,
        projectId: StrictStr,
        repo: Annotated[StrictStr, Field(description="Full repo name (owner/repo)")],
    ) -> CardProject:
        """Reads template.json and data.csv from the repo and reconstructs the CardProject object. """
        ...


    async def export_project(
        self,
        projectId: StrictStr,
        export_project_request: ExportProjectRequest,
    ) -> file:
        """Returns a zip archive of generated HTML cards, JSON-LD, template.json, and data.csv — without committing to a repo. """
        ...
