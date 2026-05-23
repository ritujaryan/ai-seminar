from typing import Optional, Dict
from app.models.session import SeminarSession
from app.repositories.base import BaseRepository

class SessionRepository(BaseRepository[SeminarSession]):
    def __init__(self):
        self._sessions: Dict[str, SeminarSession] = {}
        self._active_session_id: Optional[str] = None

    def get(self, session_id: str) -> Optional[SeminarSession]:
        return self._sessions.get(session_id)

    def get_all(self) -> list[SeminarSession]:
        return list(self._sessions.values())

    def create(self, item: SeminarSession) -> SeminarSession:
        self._sessions[item.session_id] = item
        self._active_session_id = item.session_id
        return item

    def update(self, session_id: str, item: SeminarSession) -> SeminarSession:
        if session_id in self._sessions:
            self._sessions[session_id] = item
            return item
        raise ValueError(f"Session with ID {session_id} not found")

    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            if self._active_session_id == session_id:
                self._active_session_id = None
            return True
        return False

    def get_active(self) -> Optional[SeminarSession]:
        if self._active_session_id:
            return self._sessions.get(self._active_session_id)
        return None

    def clear(self):
        self._sessions.clear()
        self._active_session_id = None

# Singleton instance
session_repo = SessionRepository()
