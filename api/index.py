"""Vercel serverless entrypoint.

Vercel's Python runtime serves an ASGI app exposed as ``app``. The package
lives under ``../src`` (not pip-installed), so we add it to the path; the
``src/**`` tree is shipped via ``includeFiles`` in vercel.json.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from openapi_server.main import app  # noqa: E402  (served by Vercel as ASGI)

__all__ = ["app"]
