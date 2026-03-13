# AI Content Generator & Auto Video Creator

A complete Python project that automatically:

1. Finds trending topics
2. Generates an AI script (OpenAI/Gemini or fallback)
3. Converts script to voice (gTTS)
4. Fetches relevant images from free APIs (Pexels/Unsplash) or placeholders
5. Creates subtitles
6. Renders a ready-to-upload MP4 video
7. Provides a simple Streamlit UI

## Folder Structure

```text
ai-video-generator-project/
├── app.py
├── modules/
│   ├── __init__.py
│   ├── script_generator.py
│   ├── voice_generator.py
│   ├── media_fetcher.py
│   ├── subtitle_generator.py
│   └── video_creator.py
├── output/
├── temp/
├── assets/
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Optional API keys

Set any of the following for enhanced generation quality:

```bash
export OPENAI_API_KEY="your_openai_key"
export GEMINI_API_KEY="your_gemini_key"
export PEXELS_API_KEY="your_pexels_key"
export UNSPLASH_ACCESS_KEY="your_unsplash_key"
```

## Run the app

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Workflow

- Select category/topic
- Generate script
- Generate voice
- Fetch media
- Auto-create subtitles
- Render final MP4 into `output/`

## Notes

- If no AI API keys are provided, the app uses a local fallback script generator.
- If no media API keys are provided, it auto-generates placeholder images.
- First render can take a while depending on CPU and ffmpeg availability.
