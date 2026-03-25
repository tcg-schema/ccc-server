# coding: utf-8

from __future__ import annotations
from pydantic import BaseModel, StrictStr
from typing import Optional


class InitiateGitHubAuth200Response(BaseModel):
    authorization_url: Optional[StrictStr] = None

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }
