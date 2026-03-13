import re
from dataclasses import dataclass


@dataclass
class SubtitleSegment:
    text: str
    start: float
    end: float


def split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def generate_subtitles(narration_text: str, total_duration: float) -> list[SubtitleSegment]:
    sentences = split_sentences(narration_text)
    if not sentences:
        return []

    word_counts = [max(len(sentence.split()), 1) for sentence in sentences]
    total_words = sum(word_counts)

    segments: list[SubtitleSegment] = []
    cursor = 0.0
    for sentence, words in zip(sentences, word_counts):
        duration = max(total_duration * (words / total_words), 0.8)
        end = min(cursor + duration, total_duration)
        segments.append(SubtitleSegment(text=sentence, start=cursor, end=end))
        cursor = end

    if segments:
        segments[-1].end = total_duration
    return segments
