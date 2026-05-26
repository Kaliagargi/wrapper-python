# core/session.py

import uuid
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd

# ── In-memory store ───────────────────────────────────────

_sessions: dict = {}
SESSION_EXPIRY_HOURS = 8  # Session lives for 8 hours


# ── Session Model ─────────────────────────────────────────

class Session:
    def __init__(self, file_path: str, df: pd.DataFrame):
        self.session_id = str(uuid.uuid4())
        self.file_path = file_path        # Path to uploaded Excel file
        self.df = df                      # Parsed clean DataFrame
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(hours=SESSION_EXPIRY_HOURS)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


# ── Session Operations ────────────────────────────────────

def create_session(file_path: str, df: pd.DataFrame) -> str:
    """Create a new session, store it, return session_id"""
    session = Session(file_path, df)
    _sessions[session.session_id] = session
    return session.session_id


def get_session(session_id: str) -> Session:
    """Fetch session by ID. Raises error if missing or expired."""
    from core.errors import SessionNotFoundError  # avoid circular import

    session = _sessions.get(session_id)

    if session is None:
        raise SessionNotFoundError()

    if session.is_expired():
        delete_session(session_id)
        raise SessionNotFoundError()

    return session


def delete_session(session_id: str) -> None:
    """Remove session from store"""
    _sessions.pop(session_id, None)


def cleanup_expired_sessions() -> int:
    """Remove all expired sessions. Returns count of removed sessions."""
    expired = [
        sid for sid, s in _sessions.items()
        if s.is_expired()
    ]
    for sid in expired:
        del _sessions[sid]
    return len(expired)


def get_active_session_count() -> int:
    return len(_sessions)