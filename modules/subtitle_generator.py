"""Simple subtitle timing generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class SubtitleSegment:
    start: float
    end: float
    text: str


class SubtitleGenerator:
    def split(self, script: str, total_duration: float, max_words: int = 8) -> List[SubtitleSegment]:
        words = script.split()
        if not words:
            return []

        chunks: List[str] = []
        for i in range(0, len(words), max_words):
            chunks.append(" ".join(words[i : i + max_words]))

        segment_duration = total_duration / max(len(chunks), 1)
        segments: List[SubtitleSegment] = []
        cursor = 0.0
        for chunk in chunks:
            end_time = cursor + segment_duration
            segments.append(SubtitleSegment(start=cursor, end=end_time, text=chunk))
            cursor = end_time
        return segments
