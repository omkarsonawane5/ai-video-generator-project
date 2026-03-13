"""Streamlit UI for AI Content Generator and Auto Video Creator."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from moviepy.editor import AudioFileClip

from modules.media_fetcher import MediaFetcher
from modules.script_generator import ScriptGenerator, TrendingTopicDetector
from modules.subtitle_generator import SubtitleGenerator
from modules.video_creator import VideoCreator
from modules.voice_generator import VoiceGenerator


st.set_page_config(page_title="AI Content + Video Creator", page_icon="🎬", layout="centered")

st.title("🎬 AI Content Generator & Auto Video Creator")
st.write(
    "Generate a complete short-form video: trending topic → AI script → voice-over → media → subtitles → MP4."
)

with st.sidebar:
    st.header("Settings")
    category = st.selectbox(
        "Category", ["technology", "motivation", "business", "health", "news"], index=0
    )
    duration = st.slider("Approx video duration (seconds)", min_value=20, max_value=90, value=45)
    media_count = st.slider("Number of visual slides", min_value=4, max_value=10, value=6)
    language = st.selectbox("Voice language", ["en", "es", "fr", "de", "hi"], index=0)

    st.caption("Optional API Keys via environment variables:")
    st.code(
        "OPENAI_API_KEY\nGEMINI_API_KEY\nPEXELS_API_KEY\nUNSPLASH_ACCESS_KEY",
        language="bash",
    )

# Workflow state
if "topics" not in st.session_state:
    detector = TrendingTopicDetector(category=category)
    st.session_state.topics = detector.get_trending_topics(limit=10)

if st.button("🔄 Refresh Trending Topics"):
    detector = TrendingTopicDetector(category=category)
    st.session_state.topics = detector.get_trending_topics(limit=10)

selected_topic = st.selectbox("Choose trending topic", st.session_state.topics)
custom_topic = st.text_input("Or type custom topic")
final_topic = custom_topic.strip() or selected_topic

if st.button("🚀 Generate Full Video"):
    with st.spinner("Generating script..."):
        script_gen = ScriptGenerator()
        script_result = script_gen.generate_script(final_topic, duration_seconds=duration)

    st.subheader("Generated Script")
    st.write(script_result.script)

    temp_dir = Path("temp")
    output_dir = Path("output")
    temp_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    with st.spinner("Creating voice-over..."):
        voice_path = temp_dir / "voice.mp3"
        voice_gen = VoiceGenerator(language=language)
        voice_gen.generate(script_result.script, str(voice_path))

    with st.spinner("Fetching media assets..."):
        fetcher = MediaFetcher(output_dir=str(temp_dir / "media"))
        media_paths = fetcher.fetch_images(final_topic, count=media_count)

    with st.spinner("Generating subtitles..."):
        audio_clip = AudioFileClip(str(voice_path))
        subtitle_gen = SubtitleGenerator()
        subtitles = subtitle_gen.split(script_result.script, total_duration=audio_clip.duration)
        audio_clip.close()

    with st.spinner("Rendering final MP4..."):
        video_creator = VideoCreator()
        safe_topic = "".join(ch for ch in final_topic if ch.isalnum() or ch in {"-", "_", " "}).strip()
        safe_topic = safe_topic.replace(" ", "_") or "generated_video"
        final_video_path = output_dir / f"{safe_topic}.mp4"
        rendered = video_creator.create_video(
            image_paths=media_paths,
            audio_path=str(voice_path),
            subtitles=subtitles,
            output_path=str(final_video_path),
        )

    st.success("Video generated successfully!")
    st.video(rendered)

    with open(rendered, "rb") as f:
        st.download_button(
            "⬇️ Download MP4",
            data=f.read(),
            file_name=os.path.basename(rendered),
            mime="video/mp4",
        )

st.markdown("---")
st.caption("Tip: Add API keys for higher quality AI script and media sources.")
