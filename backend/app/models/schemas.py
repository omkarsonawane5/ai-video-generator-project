from pydantic import BaseModel, Field
from typing import Literal

class Source(BaseModel):
    title: str
    url: str
    snippet: str = ""

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    text: str = Field(min_length=1)
    use_search: bool = False
    session_id: str = "default"

class ChatResponse(BaseModel):
    text: str
    sources: list[Source] = []
    session_id: str

class SettingsUpdate(BaseModel):
    openai_api_key: str | None = None
    openai_model: str | None = None
    openai_voice: str | None = None
