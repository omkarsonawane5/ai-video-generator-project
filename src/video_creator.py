from datetime import datetime
from pathlib import Path
from typing import Callable

from moviepy import AudioFileClip, ColorClip, CompositeAudioClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

from src.config import Paths, VideoSettings
from src.logger import setup_logger
from src.subtitle_generator import SubtitleSegment, generate_subtitles

logger = setup_logger()

ProgressCallback = Callable[[float, str], None]


class VideoCreator:
    def __init__(self, paths: Paths) -> None:
        self.paths = paths
        self.paths.ensure()

    def create_video(
        self,
        script_title: str,
        narration_text: str,
        voiceover_path: Path,
        settings: VideoSettings,
        bgm_path: Path | None,
        progress: ProgressCallback,
    ) -> Path:
        width, height = settings.resolution
        progress(0.55, "Loading audio")
        narration_clip = AudioFileClip(str(voiceover_path))
        duration = min(max(narration_clip.duration, 8), settings.duration_seconds + 20)

        progress(0.65, "Generating subtitle timeline")
        subtitles = generate_subtitles(narration_text, duration)

        progress(0.75, "Composing styled captions")
        background = ColorClip(size=(width, height), color=(20, 22, 30), duration=duration)
        subtitle_clips = self._subtitle_overlays(subtitles, width, height)
        title_clip = self._title_overlay(script_title, width, height, min(4, duration))

        layers = [background, title_clip, *subtitle_clips]
        final_video = CompositeVideoClip(layers).set_duration(duration)

        audio_layers = [narration_clip.volumex(1.0)]
        if settings.include_bgm and bgm_path and bgm_path.exists():
            try:
                bgm_clip = AudioFileClip(str(bgm_path)).audio_loop(duration=duration).volumex(settings.bgm_volume)
                audio_layers.append(bgm_clip)
            except Exception as exc:
                logger.warning("Background music skipped: %s", exc)

        final_video = final_video.set_audio(CompositeAudioClip(audio_layers))

        output_name = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_path = self.paths.outputs / output_name

        progress(0.9, "Rendering final video")
        final_video.write_videofile(
            str(output_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )
        progress(1.0, "Video ready")
        return output_path

    def _subtitle_overlays(self, segments: list[SubtitleSegment], width: int, height: int) -> list[ImageClip]:
        clips: list[ImageClip] = []
        for idx, segment in enumerate(segments):
            image_path = self.paths.temp / f"subtitle_{idx}.png"
            self._build_caption_image(segment.text, width, height, image_path)
            clip = (
                ImageClip(str(image_path))
                .set_start(segment.start)
                .set_end(segment.end)
                .set_position(("center", int(height * 0.78)))
            )
            clips.append(clip)
        return clips

    def _title_overlay(self, title: str, width: int, height: int, duration: float) -> ImageClip:
        image_path = self.paths.temp / "title.png"
        self._build_caption_image(title, width, height, image_path, title_style=True)
        return ImageClip(str(image_path)).set_start(0).set_end(duration).set_position(("center", int(height * 0.12)))

    def _build_caption_image(self, text: str, width: int, height: int, output_path: Path, title_style: bool = False) -> None:
        canvas = Image.new("RGBA", (width, int(height * 0.2)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        font_size = max(32, width // 28) if not title_style else max(42, width // 22)
        with_title = "bold" if title_style else "regular"
        font = self._load_font(font_size, with_title)

        lines = self._wrap_text(text, draw, font, int(width * 0.8))
        line_height = font_size + 12
        box_height = line_height * len(lines) + 26
        y0 = max((canvas.height - box_height) // 2, 10)
        x0 = int(width * 0.08)
        x1 = int(width * 0.92)
        y1 = min(y0 + box_height, canvas.height - 10)

        fill = (124, 58, 237, 230) if title_style else (17, 24, 39, 210)
        draw.rounded_rectangle([(x0, y0), (x1, y1)], radius=24, fill=fill)

        y_text = y0 + 14
        for line in lines:
            text_width = draw.textbbox((0, 0), line, font=font)[2]
            x_text = (width - text_width) // 2
            draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255, 255))
            y_text += line_height

        canvas.save(output_path)

    @staticmethod
    def _wrap_text(text: str, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
        words = text.split()
        if not words:
            return [""]

        lines: list[str] = []
        current_line = words[0]
        for word in words[1:]:
            candidate = f"{current_line} {word}"
            w = draw.textbbox((0, 0), candidate, font=font)[2]
            if w <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines[:3]

    @staticmethod
    def _load_font(font_size: int, style: str) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        preferred = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if style == "bold" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        for candidate in preferred:
            path = Path(candidate)
            if path.exists():
                return ImageFont.truetype(str(path), font_size)
        return ImageFont.load_default()
