from collections import defaultdict, deque
from backend.app.models.schemas import ChatMessage

class SessionMemory:
    def __init__(self, max_messages: int = 20) -> None:
        self._messages: dict[str, deque[ChatMessage]] = defaultdict(lambda: deque(maxlen=max_messages))

    def add(self, session_id: str, role: str, content: str) -> None:
        self._messages[session_id].append(ChatMessage(role=role, content=content))

    def history(self, session_id: str) -> list[ChatMessage]:
        return list(self._messages[session_id])

    def clear(self, session_id: str) -> None:
        self._messages.pop(session_id, None)
