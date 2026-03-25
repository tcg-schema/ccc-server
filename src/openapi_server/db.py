"""Tortoise ORM models and DB helper functions."""

import os
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional

from tortoise import connections, fields, models

SESSION_EXPIRY_HOURS = int(os.environ.get("SESSION_EXPIRY_HOURS", "24"))


# ── Models ────────────────────────────────────────────────────────────────────

class Session(models.Model):
    session_token = fields.CharField(max_length=128, pk=True)
    github_access_token = fields.TextField()
    user_login = fields.CharField(max_length=200)
    user_name = fields.CharField(max_length=200, null=True)
    user_avatar_url = fields.CharField(max_length=500, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "sessions"


class OAuthState(models.Model):
    state = fields.CharField(max_length=128, pk=True)
    return_to = fields.CharField(max_length=2000, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "oauth_states"


class ProjectSave(models.Model):
    id = fields.IntField(pk=True)
    user_login = fields.CharField(max_length=200)
    project_id = fields.CharField(max_length=100)
    project_name = fields.CharField(max_length=500)
    repo = fields.CharField(max_length=500)
    saved_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "project_saves"


# ── OAuth state ───────────────────────────────────────────────────────────────

async def create_oauth_state(return_to: Optional[str]) -> str:
    state = secrets.token_urlsafe(32)
    await OAuthState.create(state=state, return_to=return_to)
    return state


async def consume_oauth_state(state: str) -> Optional[str]:
    """Delete and return `return_to` if the state is valid and <10 min old."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    obj = await OAuthState.filter(state=state, created_at__gte=cutoff).first()
    if obj is None:
        return None
    return_to = obj.return_to
    await obj.delete()
    return return_to


# ── Sessions ──────────────────────────────────────────────────────────────────

async def create_session(
    github_access_token: str,
    user_login: str,
    user_name: Optional[str],
    user_avatar_url: Optional[str],
) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRY_HOURS)
    await Session.create(
        session_token=token,
        github_access_token=github_access_token,
        user_login=user_login,
        user_name=user_name,
        user_avatar_url=user_avatar_url,
        expires_at=expires_at,
    )
    return token, expires_at


async def delete_session(session_token: str) -> None:
    await Session.filter(session_token=session_token).delete()


# ── Project saves ─────────────────────────────────────────────────────────────

async def record_save(
    user_login: str, project_id: str, project_name: str, repo: str
) -> None:
    await ProjectSave.create(
        user_login=user_login,
        project_id=project_id,
        project_name=project_name,
        repo=repo,
    )


# ── Stats ─────────────────────────────────────────────────────────────────────

async def get_stats() -> dict:
    now = datetime.now(timezone.utc)
    active_sessions = await Session.filter(expires_at__gt=now).count()
    sessions_today = await Session.filter(
        created_at__gte=now - timedelta(hours=24)
    ).count()
    total_saves = await ProjectSave.all().count()

    conn = connections.get("default")
    _, users_rows = await conn.execute_query(
        "SELECT COUNT(DISTINCT user_login) AS n FROM sessions"
    )
    total_users = users_rows[0]["n"] if users_rows else 0

    _, top_rows = await conn.execute_query(
        "SELECT user_login, COUNT(*) AS saves FROM project_saves "
        "GROUP BY user_login ORDER BY saves DESC LIMIT 10"
    )
    _, recent_rows = await conn.execute_query(
        "SELECT user_login, project_name, repo, saved_at "
        "FROM project_saves ORDER BY saved_at DESC LIMIT 20"
    )

    return {
        "active_sessions": active_sessions,
        "total_users": total_users,
        "sessions_today": sessions_today,
        "total_saves": total_saves,
        "top_users": [dict(r) for r in top_rows],
        "recent_saves": [dict(r) for r in recent_rows],
    }
