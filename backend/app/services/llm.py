from collections.abc import AsyncIterator
from openai import AsyncOpenAI
from fastapi import HTTPException
from backend.app.core.config import get_settings
from backend.app.models.schemas import ChatMessage, Source

class LLMProvider:
    async def complete(self, messages: list[ChatMessage], sources: list[Source] | None = None) -> str:
        raise NotImplementedError
    async def stream(self, messages: list[ChatMessage], sources: list[Source] | None = None) -> AsyncIterator[str]:
        raise NotImplementedError

class OpenAIResponsesProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key
        self.client: AsyncOpenAI | None = None

    def _client(self) -> AsyncOpenAI:
        if not self.api_key:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY is required. Add it to .env or settings.")
        if self.client is None:
            self.client = AsyncOpenAI(api_key=self.api_key)
        return self.client

    def _input(self, messages: list[ChatMessage], sources: list[Source] | None) -> str:
        source_block = ""
        if sources:
            source_block = "\n\nSources to use and cite:\n" + "\n".join(f"- {s.title}: {s.url}\n  {s.snippet}" for s in sources)
        return "\n".join(f"{m.role}: {m.content}" for m in messages) + source_block

    async def complete(self, messages: list[ChatMessage], sources: list[Source] | None = None) -> str:
        client = self._client()
        response = await client.responses.create(model=self.model, input=self._input(messages, sources))
        return response.output_text

    async def stream(self, messages: list[ChatMessage], sources: list[Source] | None = None) -> AsyncIterator[str]:
        client = self._client()
        async with client.responses.stream(model=self.model, input=self._input(messages, sources)) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta
