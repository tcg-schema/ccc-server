# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBytes, StrictStr  # noqa: F401
from typing import Any, Tuple, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.card_project import CardProject  # noqa: F401
from openapi_server.models.export_project_request import ExportProjectRequest  # noqa: F401
from openapi_server.models.save_project_request import SaveProjectRequest  # noqa: F401
from openapi_server.models.save_project_response import SaveProjectResponse  # noqa: F401


def test_save_project(client: TestClient):
    """Test case for save_project

    Save a CardForge project to a GitHub repo
    """
    save_project_request = {"repo":"octocat/my-cards","project":{"created_at":"2000-01-23T04:56:07.000+00:00","sheets":[{"template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490},"name":"name","id":"id","rows":[null,null],"back_template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490}},{"template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490},"name":"name","id":"id","rows":[null,null],"back_template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490}}],"name":"name","description":"description","is_public":1,"id":"id"},"branch":"branch"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/projects/{projectId}/save".format(projectId='project_id_example'),
    #    headers=headers,
    #    json=save_project_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_load_project(client: TestClient):
    """Test case for load_project

    Load a CardForge project from a GitHub repo
    """
    params = [("repo", 'repo_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/projects/{projectId}/load".format(projectId='project_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_export_project(client: TestClient):
    """Test case for export_project

    Export rendered cards without saving to GitHub
    """
    export_project_request = {"project":{"created_at":"2000-01-23T04:56:07.000+00:00","sheets":[{"template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490},"name":"name","id":"id","rows":[null,null],"back_template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490}},{"template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490},"name":"name","id":"id","rows":[null,null],"back_template":{"background_color":"hsl(220 18% 13%)","background_image":"backgroundImage","elements":[{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182},{"tcg_type":"tcgType","tcg_property":"tcgProperty","x":0.8008281904610115,"width":1.4658129805029452,"y":6.027456183070403,"style":{"stroke_width":2.3021358869347655,"color":"color","icon_name":"iconName","image_url":"https://openapi-generator.tech","rotation":7.061401241503109,"font_size":5.637376656633329,"svg_data":"svgData","font_weight":"fontWeight"},"id":"id","tag":"tag","type":"text","visible_if_field":"visibleIfField","height":5.962133916683182}],"name":"name","width":350,"id":"id","height":490}}],"name":"name","description":"description","is_public":1,"id":"id"}}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/projects/{projectId}/export".format(projectId='project_id_example'),
    #    headers=headers,
    #    json=export_project_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

