from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.config import Paths, VideoSettings
from src.content_generator import ContentGenerator, build_narration_text
from src.logger import setup_logger
from src.video_creator import VideoCreator
from src.voice_generator import VOICE_OPTIONS, VoiceGenerator

load_dotenv()
logger = setup_logger()

st.set_page_config(page_title="AI Content Generator + Auto Video Creator", page_icon="🎬", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg, #111827, #1f2937);}
    .hero {padding: 16px 18px; border-radius: 16px; background: linear-gradient(130deg,#4f46e5,#9333ea); color: white;}
    .metric-card {padding: 12px; border:1px solid #2d3748; border-radius:12px; background:#111827;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='hero'><h2>🎥 AI Content Generator & Auto Video Creator</h2><p>Final-year project-ready dashboard for automated short video production.</p></div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Content Setup")
    topic = st.text_input("Video Topic", placeholder="e.g., Impact of AI in Healthcare")
    tone = st.selectbox("Tone", ["Professional", "Storytelling", "Energetic", "Educational"])
    duration_seconds = st.slider("Target Duration (seconds)", min_value=20, max_value=120, value=45)
    orientation = st.radio("Video Mode", ["Standard (16:9)", "YouTube Shorts (9:16)"], horizontal=True)

with col2:
    st.subheader("Audio & Render")
    voice_name = st.selectbox("AI Voice", list(VOICE_OPTIONS.keys()))
    include_bgm = st.toggle("Add Background Music", value=True)
    bgm_volume = st.slider("Background Music Volume", 0.05, 0.7, 0.2, 0.05)
    bgm_upload = st.file_uploader("Upload optional BGM (mp3/wav)", type=["mp3", "wav", "m4a"])

if st.button("🚀 Generate Video", type="primary", use_container_width=True):
    if not topic.strip():
        st.error("Please enter a topic before generating the video.")
    else:
        try:
            paths = Paths()
            paths.ensure()

            settings = VideoSettings(
                topic=topic,
                tone=tone,
                duration_seconds=duration_seconds,
                voice_name=voice_name,
                orientation=orientation,
                include_bgm=include_bgm,
                bgm_volume=bgm_volume,
            )

            progress_bar = st.progress(0.0, text="Initializing")

            def update_progress(value: float, label: str) -> None:
                progress_bar.progress(min(max(value, 0.0), 1.0), text=label)

            update_progress(0.1, "Generating AI script")
            content_generator = ContentGenerator()
            script_data = content_generator.generate_script(topic, tone, duration_seconds)
            narration_text = build_narration_text(script_data)

            with st.expander("Generated Script", expanded=False):
                st.markdown(f"### {script_data.get('title', 'Generated Title')}")
                st.write(script_data.get("hook", ""))
                for item in script_data.get("sections", []):
                    st.write(f"- {item}")
                st.caption(script_data.get("cta", ""))

            update_progress(0.35, "Synthesizing AI voice")
            voice_path = paths.temp / "voiceover.mp3"
            voice_generator = VoiceGenerator()
            narration_audio = voice_generator.generate_voiceover(narration_text, voice_name, voice_path)

            bgm_path = None
            if include_bgm and bgm_upload:
                bgm_path = paths.temp / f"bgm_{bgm_upload.name}"
                with open(bgm_path, "wb") as f:
                    f.write(bgm_upload.read())

            video_creator = VideoCreator(paths)
            video_path = video_creator.create_video(
                script_title=script_data.get("title", topic.title()),
                narration_text=narration_text,
                voiceover_path=narration_audio,
                settings=settings,
                bgm_path=bgm_path,
                progress=update_progress,
            )

            st.success("Video generated successfully!")
            st.video(str(video_path))
            with open(video_path, "rb") as file:
                st.download_button(
                    label="⬇️ Download Final Video",
                    data=file,
                    file_name=Path(video_path).name,
                    mime="video/mp4",
                    use_container_width=True,
                )
        except Exception as exc:
            logger.exception("Generation failed: %s", exc)
            st.error(f"Failed to generate video: {exc}")

st.divider()
metric_cols = st.columns(4)
metric_cols[0].markdown("<div class='metric-card'>✅ Dashboard UI</div>", unsafe_allow_html=True)
metric_cols[1].markdown("<div class='metric-card'>🎬 Shorts Support</div>", unsafe_allow_html=True)
metric_cols[2].markdown("<div class='metric-card'>🧠 AI Script + Voice</div>", unsafe_allow_html=True)
metric_cols[3].markdown("<div class='metric-card'>📝 Styled Subtitles</div>", unsafe_allow_html=True)
