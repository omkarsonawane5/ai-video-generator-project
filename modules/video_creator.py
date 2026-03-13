"""Compose voice, media and subtitles into an MP4 video."""

from __future__ import annotations

from pathlib import Path
from typing import List

import cv2
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
)

from modules.subtitle_generator import SubtitleSegment


class VideoCreator:
    def __init__(self, width: int = 1080, height: int = 1920) -> None:
        self.width = width
        self.height = height

    def create_video(
        self,
        image_paths: List[str],
        audio_path: str,
        subtitles: List[SubtitleSegment],
        output_path: str,
        fps: int = 24,
    ) -> str:
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration

        clip_duration = total_duration / max(len(image_paths), 1)
        image_clips = [
            self._build_image_clip(path, clip_duration) for path in image_paths
        ]

        base_video = concatenate_videoclips(image_clips, method="compose").set_audio(audio)
        subtitle_clips = [self._subtitle_clip(segment) for segment in subtitles]

        final = CompositeVideoClip([base_video, *subtitle_clips], size=(self.width, self.height))

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(
            str(out),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None,
        )

        final.close()
        audio.close()
        for clip in image_clips:
            clip.close()

        return str(out)

    def _build_image_clip(self, image_path: str, duration: float) -> ImageClip:
        prepared_image = self._prepare_image(image_path)
        return (
            ImageClip(prepared_image)
            .set_duration(duration)
            .resize((self.width, self.height))
            .fadein(0.3)
            .fadeout(0.3)
        )

    def _prepare_image(self, image_path: str) -> str:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        src_h, src_w = image.shape[:2]
        src_ratio = src_w / src_h
        target_ratio = self.width / self.height

        if src_ratio > target_ratio:
            new_w = int(src_h * target_ratio)
            x1 = (src_w - new_w) // 2
            cropped = image[:, x1 : x1 + new_w]
        else:
            new_h = int(src_w / target_ratio)
            y1 = (src_h - new_h) // 2
            cropped = image[y1 : y1 + new_h, :]

        resized = cv2.resize(cropped, (self.width, self.height), interpolation=cv2.INTER_AREA)

        temp_out = Path(image_path).with_suffix(".processed.jpg")
        cv2.imwrite(str(temp_out), cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
        return str(temp_out)

    def _subtitle_clip(self, segment: SubtitleSegment) -> TextClip:
        return (
            TextClip(
                segment.text,
                fontsize=56,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                align="center",
                size=(self.width - 120, None),
                font="DejaVu-Sans",
            )
            .set_start(segment.start)
            .set_end(segment.end)
            .set_position(("center", self.height - 360))
        )
