from pathlib import Path
from openai import AsyncOpenAI
from fastapi import HTTPException
from backend.app.core.config import get_settings

class SpeechService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: AsyncOpenAI | None = None

    def _client(self) -> AsyncOpenAI:
        if not self.settings.openai_api_key:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY is required for speech services.")
        if self.client is None:
            self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        return self.client

    async def transcribe(self, audio_path: Path) -> str:
        with audio_path.open("rb") as audio_file:
            result = await self._client().audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=audio_file)
        return result.text

    async def synthesize(self, text: str, output_path: Path) -> Path:
        response = await self._client().audio.speech.create(model="gpt-4o-mini-tts", voice=self.settings.openai_voice, input=text)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await response.astream_to_file(output_path)
        return output_path
