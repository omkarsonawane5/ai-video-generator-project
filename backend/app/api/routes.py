from pathlib import Path
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from backend.app.core.config import get_settings
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.services.assistant import AssistantService
from backend.app.services.audio import SpeechService
from backend.app.services.search import SearchService

router = APIRouter()
assistant = AssistantService()
speech = SpeechService()
search = SearchService()

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return await assistant.ask(request.text, request.session_id, request.use_search)

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def events():
        response = await assistant.ask(request.text, request.session_id, request.use_search)
        for token in response.text.split(" "):
            yield f"data: {token} \n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")

@router.post("/speech/transcribe")
async def transcribe(file: UploadFile = File(...)) -> dict[str, str]:
    target = get_settings().data_dir / "audio" / file.filename
    target.write_bytes(await file.read())
    return {"text": await speech.transcribe(target)}

@router.post("/speech/synthesize")
async def synthesize(payload: dict[str, str]) -> FileResponse:
    path = get_settings().data_dir / "audio" / "reply.mp3"
    await speech.synthesize(payload["text"], path)
    return FileResponse(path, media_type="audio/mpeg")

@router.get("/web/summarize")
async def summarize(url: str) -> ChatResponse:
    text = await search.fetch_page_text(url)
    return await assistant.ask(f"Summarize this webpage and extract key facts:\n{text}", "web", False)
