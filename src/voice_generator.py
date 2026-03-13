import asyncio
import contextlib
import wave
from pathlib import Path

import edge_tts

from src.logger import setup_logger

logger = setup_logger()

VOICE_OPTIONS = {
    "Aria (English - Female)": "en-US-AriaNeural",
    "Guy (English - Male)": "en-US-GuyNeural",
    "Jenny (English - Female)": "en-US-JennyNeural",
    "Ryan (UK - Male)": "en-GB-RyanNeural",
}


class VoiceGenerator:
    async def _synthesize(self, text: str, voice_id: str, output_path: Path) -> None:
        communicate = edge_tts.Communicate(text=text, voice=voice_id)
        await communicate.save(str(output_path))

    def generate_voiceover(self, text: str, voice_name: str, output_path: Path) -> Path:
        voice_id = VOICE_OPTIONS.get(voice_name, "en-US-AriaNeural")
        try:
            asyncio.run(self._synthesize(text, voice_id, output_path))
            return output_path
        except Exception as exc:
            logger.exception("Voice synthesis failed, creating silent fallback audio: %s", exc)
            return self._silent_fallback(output_path)

    def _silent_fallback(self, output_path: Path, duration_seconds: int = 10) -> Path:
        wav_path = output_path.with_suffix(".wav")
        with contextlib.closing(wave.open(str(wav_path), "w")) as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(b"\x00\x00" * 22050 * duration_seconds)
        return wav_path
