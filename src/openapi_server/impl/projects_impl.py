import json

from fastapi import HTTPException
from fastapi.responses import Response

from openapi_server.apis.projects_api_base import BaseProjectsApi
from openapi_server.card_renderer import _card_html, _csv, _jsonld, project_to_zip
from openapi_server.db import record_save
from openapi_server.github_client import commit_files, get_file
from openapi_server.models.card_project import CardProject
from openapi_server.models.save_project_response import SaveProjectResponse
from openapi_server.security_api import current_session


class ProjectsApiImpl(BaseProjectsApi):
    async def save_project(self, projectId, save_project_request):
        sess = current_session.get()
        req = save_project_request
        project = req.project

        folder = f"cardforge/{project.id}"
        files: dict[str, bytes] = {
            f"{folder}/project.json": json.dumps(project.to_dict(), indent=2).encode(),
        }

        for sheet in project.sheets:
            sf = sheet.name.replace(" ", "_")
            files[f"{folder}/{sf}/template.json"] = json.dumps(
                sheet.template.to_dict(), indent=2
            ).encode()
            if sheet.rows:
                files[f"{folder}/{sf}/data.csv"] = _csv(sheet.rows).encode()
            files[f"{folder}/{sf}/data.json"] = json.dumps(sheet.rows, indent=2).encode()
            for i, row in enumerate(sheet.rows):
                files[f"{folder}/{sf}/card_{i + 1}.html"] = _card_html(
                    sheet.template, row
                ).encode()

        ld = _jsonld(project)
        if ld:
            files[f"{folder}/cards.jsonld"] = json.dumps(ld, indent=2).encode()

        await commit_files(
            access_token=sess["github_access_token"],
            repo=req.repo,
            branch=req.branch,
            files=files,
            message=f"CardForge: save {project.name}",
        )
        await record_save(
            user_login=sess["user_login"],
            project_id=project.id,
            project_name=project.name,
            repo=req.repo,
        )
        return SaveProjectResponse(path=folder, file_count=len(files))

    async def load_project(self, projectId, repo):
        sess = current_session.get()
        result = await get_file(
            sess["github_access_token"], repo, f"cardforge/{projectId}/project.json"
        )
        if result is None:
            raise HTTPException(status_code=404, detail="Project not found in repo")
        content_bytes, _ = result
        return CardProject.from_dict(json.loads(content_bytes.decode()))

    async def export_project(self, projectId, export_project_request):
        project = export_project_request.project
        zip_bytes = project_to_zip(project)
        filename = project.name.replace(" ", "_") + ".zip"
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
