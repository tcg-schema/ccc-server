"""Simple admin stats page — secured by ADMIN_TOKEN env var."""

import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from openapi_server.db import get_stats

router = APIRouter()

_ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")


def _check_token(token: str) -> None:
    if not _ADMIN_TOKEN:
        raise HTTPException(status_code=503, detail="Admin not configured (set ADMIN_TOKEN)")
    if token != _ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _render(stats: dict) -> str:
    top_rows = "".join(
        f"<tr><td>{r['user_login']}</td><td>{r['saves']}</td></tr>"
        for r in stats["top_users"]
    )
    recent_rows = "".join(
        f"<tr><td>{r['user_login']}</td><td>{r['project_name']}</td>"
        f"<td>{r['repo']}</td><td>{r['saved_at']}</td></tr>"
        for r in stats["recent_saves"]
    )
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CardForge Admin</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 40px auto;
            padding: 0 20px; background: #f5f5f5; color: #222; }}
    h1 {{ margin-bottom: 4px; }}
    .ts {{ color: #888; font-size: .85em; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 32px; }}
    .card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
             padding: 18px 20px; }}
    .val {{ font-size: 2.2em; font-weight: 700; color: #2563eb; line-height: 1; }}
    .lbl {{ color: #666; font-size: .85em; margin-top: 4px; }}
    h2 {{ font-size: 1em; text-transform: uppercase; letter-spacing: .05em;
          color: #555; margin: 24px 0 8px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff;
             border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 9px 14px; text-align: left; border-bottom: 1px solid #eee;
               font-size: .9em; }}
    th {{ background: #f3f4f6; font-weight: 600; color: #444; }}
    tr:last-child td {{ border-bottom: none; }}
  </style>
</head>
<body>
  <h1>CardForge Admin</h1>
  <div class="ts">Generated {generated}</div>
  <div class="grid">
    <div class="card"><div class="val">{stats["active_sessions"]}</div>
      <div class="lbl">Active sessions</div></div>
    <div class="card"><div class="val">{stats["total_users"]}</div>
      <div class="lbl">Unique users (all time)</div></div>
    <div class="card"><div class="val">{stats["sessions_today"]}</div>
      <div class="lbl">New sessions (24 h)</div></div>
    <div class="card"><div class="val">{stats["total_saves"]}</div>
      <div class="lbl">Total project saves</div></div>
  </div>

  <h2>Top users by saves</h2>
  <table>
    <thead><tr><th>User</th><th>Saves</th></tr></thead>
    <tbody>{top_rows or "<tr><td colspan='2'>No saves yet</td></tr>"}</tbody>
  </table>

  <h2>Recent saves</h2>
  <table>
    <thead><tr><th>User</th><th>Project</th><th>Repo</th><th>Time (UTC)</th></tr></thead>
    <tbody>{recent_rows or "<tr><td colspan='4'>No saves yet</td></tr>"}</tbody>
  </table>
</body>
</html>"""


@router.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def admin_stats(token: str = Query(..., description="Admin token")):
    _check_token(token)
    stats = await get_stats()
    return HTMLResponse(_render(stats))
