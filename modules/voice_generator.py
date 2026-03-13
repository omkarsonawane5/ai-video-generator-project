"""Voice generation using gTTS."""

from __future__ import annotations

from pathlib import Path

from gtts import gTTS


class VoiceGenerator:
    def __init__(self, language: str = "en") -> None:
        self.language = language

    def generate(self, text: str, output_path: str) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        tts = gTTS(text=text, lang=self.language)
        tts.save(str(output))
        return str(output)
