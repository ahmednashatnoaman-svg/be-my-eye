from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock

from app.schemas.common import ConversationTurn


@dataclass
class InMemorySessionStore:
    _sessions: dict[str, list[ConversationTurn]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def get_history(self, session_id: str) -> list[ConversationTurn]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def append_turn(self, session_id: str, turn: ConversationTurn) -> None:
        with self._lock:
            self._sessions.setdefault(session_id, []).append(turn)

