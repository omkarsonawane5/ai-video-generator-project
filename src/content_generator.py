import json
import os
from typing import Any

from openai import OpenAI

from src.logger import setup_logger

logger = setup_logger()


class ContentGenerator:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_script(self, topic: str, tone: str, duration_seconds: int) -> dict[str, Any]:
        if self.client:
            try:
                return self._generate_with_openai(topic, tone, duration_seconds)
            except Exception as exc:
                logger.exception("OpenAI generation failed, using fallback: %s", exc)
        return self._fallback_script(topic, tone, duration_seconds)

    def _generate_with_openai(self, topic: str, tone: str, duration_seconds: int) -> dict[str, Any]:
        prompt = (
            "Create a short educational video script as JSON with keys: "
            "title, hook, sections (list of strings), cta. "
            f"Topic: {topic}. Tone: {tone}. Length target: {duration_seconds} seconds."
        )
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0.7,
            max_output_tokens=700,
        )
        raw = response.output_text
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from model; wrapping as plain script")
            return {
                "title": f"{topic.title()} Explained",
                "hook": raw[:140],
                "sections": [raw],
                "cta": "Like, share, and subscribe for more!",
            }

    def _fallback_script(self, topic: str, tone: str, duration_seconds: int) -> dict[str, Any]:
        section_count = 4 if duration_seconds > 50 else 3
        sections = [
            f"Point {i + 1}: A {tone.lower()} insight about {topic} and why it matters in real-world applications."
            for i in range(section_count)
        ]
        return {
            "title": f"{topic.title()} in {duration_seconds} Seconds",
            "hook": f"What if you could understand {topic} in one short video? Let's break it down.",
            "sections": sections,
            "cta": "Follow for more smart, quick explainers!",
        }


def build_narration_text(script_data: dict[str, Any]) -> str:
    parts = [script_data.get("hook", "")]
    parts.extend(script_data.get("sections", []))
    parts.append(script_data.get("cta", ""))
    return " ".join(part.strip() for part in parts if part).strip()
