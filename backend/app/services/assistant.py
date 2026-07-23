from backend.app.core.config import get_settings
from backend.app.models.schemas import ChatResponse
from backend.app.services.llm import OpenAIResponsesProvider
from backend.app.services.memory import SessionMemory
from backend.app.services.search import SearchService

class AssistantService:
    def __init__(self) -> None:
        settings = get_settings()
        self.memory = SessionMemory(settings.max_history_messages)
        self.search = SearchService()
        self.llm = OpenAIResponsesProvider()
        self.system_prompt = "You are a warm, fast, conversational AI voice assistant. For current information, use supplied web sources and include concise source links."

    async def ask(self, text: str, session_id: str = "default", use_search: bool = False) -> ChatResponse:
        sources = self.search.search(text) if use_search else []
        self.memory.add(session_id, "user", text)
        messages = self.memory.history(session_id)
        messages.insert(0, type(messages[0])(role="system", content=self.system_prompt))
        answer = await self.llm.complete(messages, sources)
        self.memory.add(session_id, "assistant", answer)
        return ChatResponse(text=answer, sources=sources, session_id=session_id)
