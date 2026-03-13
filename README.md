# AI Content Generator & Auto Video Creator

A demo-ready final year project built with **Streamlit** that generates AI scripts and auto-creates narrated videos.

## Features
- Modern Streamlit dashboard with responsive layout
- Generate **standard (16:9)** or **YouTube Shorts (9:16)** videos
- Automatic subtitle generation with styled caption overlays
- Multiple AI voice options (Microsoft Edge TTS voices)
- Optional background music integration with audio balancing
- Real-time progress bar during generation
- Download button for final rendered video
- Structured logging and improved error handling

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── config.py
│   ├── content_generator.py
│   ├── logger.py
│   ├── subtitle_generator.py
│   ├── video_creator.py
│   └── voice_generator.py
└── outputs/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Optional API Enhancements
Set environment variables for higher-quality AI text generation:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default: `gpt-4o-mini`)

If keys are unavailable, the app falls back to an internal structured generator.

## Notes
- The app uses `edge-tts` for voice generation; internet access is required for synthesis.
- Generated videos are saved in `outputs/`.
- Logs are saved to `logs/app.log`.
