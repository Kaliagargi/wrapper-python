# core/session.py

import uuid
from datetime import datetime, timedelta
import pandas as pd

SESSION_EXPIRY_HOURS = 8

_sessions: dict = {}


# ─────────────────────────────────────────────
# SESSION MODEL
# ─────────────────────────────────────────────

class Session:
    def __init__(
        self,
        file_path:      str,
        project_layout: list,
        records:        list,
        sw_agg:         dict,
    ):
        self.session_id     = str(uuid.uuid4())
        self.file_path      = file_path       # original uploaded file path
        self.project_layout = project_layout  # list of project dicts
        self.records        = records         # all dept-level rows
        self.sw_agg         = sw_agg          # grouped by software
        self.created_at     = datetime.now()
        self.expires_at     = datetime.now() + timedelta(hours=SESSION_EXPIRY_HOURS)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


# ─────────────────────────────────────────────
# SESSION OPERATIONS
# ─────────────────────────────────────────────

def create_session(
    file_path:      str,
    project_layout: list,
    records:        list,
    sw_agg:         dict,
) -> str:
    """Create new session, return session_id"""
    session = Session(file_path, project_layout, records, sw_agg)
    _sessions[session.session_id] = session
    return session.session_id


def get_session(session_id: str) -> Session:
    """Fetch session — raises error if missing or expired"""
    from core.errors import SessionNotFoundError

    session = _sessions.get(session_id)

    if session is None:
        raise SessionNotFoundError()

    if session.is_expired():
        delete_session(session_id)
        raise SessionNotFoundError()

    return session


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def cleanup_expired_sessions() -> int:
    expired = [
        sid for sid, s in _sessions.items()
        if s.is_expired()
    ]
    for sid in expired:
        del _sessions[sid]
    return len(expired)