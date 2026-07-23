# AI Voice Assistant for Windows

Production-ready Python 3.12+ voice assistant with a FastAPI backend and React/Electron desktop UI. It supports microphone input, OpenAI STT/TTS, OpenAI Responses API chat, session memory, web search with sources, webpage summarization, dark mode UI, waveform animation, and conversation export.

## Architecture

```text
backend/app/          FastAPI API, settings, LLM, speech, search, memory services
frontend/src/         React desktop interface used by Electron
config/               Example TOML configuration
run_backend.py        Local backend launcher
package.json          Vite/Electron frontend scripts
requirements.txt      Python dependencies
```

The LLM layer uses a provider interface (`LLMProvider`) with `OpenAIResponsesProvider` as the default so Anthropic, local, or enterprise providers can be added later without changing routes.

## Features

- Always-available push-to-talk microphone flow in the desktop UI.
- Speech-to-text with OpenAI transcription.
- Conversational responses through the OpenAI Responses API.
- Natural text-to-speech playback with interruptible browser audio support.
- Session memory and bounded context history.
- Web search for recent information using DuckDuckGo Search.
- Source links returned with web answers.
- Webpage fetch and summarization endpoint.
- Modern dark React UI with chat history, mic button, waveform, settings placeholder, and export.
- Async FastAPI services, typed Pydantic models, logging, and environment configuration.

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env and set OPENAI_API_KEY
python run_backend.py
```

In another terminal:

```powershell
npm install
npm run dev
npm run electron
```

## API

- `GET /api/health` health check.
- `POST /api/chat` JSON chat with optional `use_search`.
- `POST /api/chat/stream` server-sent event compatible streaming endpoint.
- `POST /api/speech/transcribe` upload audio and receive transcript.
- `POST /api/speech/synthesize` receive MP3 speech for text.
- `GET /api/web/summarize?url=...` summarize and extract webpage information.

## Environment

See `.env.example` and `config/config.example.toml` for runtime configuration. Keep real API keys out of source control.

## Extending Providers

Implement `LLMProvider.complete()` and `LLMProvider.stream()` in `backend/app/services/llm.py`, then inject the provider in `AssistantService`. Speech providers can be swapped behind `SpeechService` in the same style.
