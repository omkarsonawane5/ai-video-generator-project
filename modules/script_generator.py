"""Generate scripts and discover trending topics for short-form videos."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class ScriptResult:
    topic: str
    script: str


class TrendingTopicDetector:
    """Fetches trending topics from public feeds with graceful fallback."""

    def __init__(self, category: str = "technology") -> None:
        self.category = category

    def get_trending_topics(self, limit: int = 10) -> List[str]:
        # Hacker News works well for tech trends and does not require API keys.
        if self.category.lower() in {"technology", "tech", "programming"}:
            topics = self._fetch_hackernews(limit)
            if topics:
                return topics

        # Generic fallback topics.
        return [
            f"Top {self.category.title()} Trends in 2026",
            f"What is changing in {self.category.title()} this week",
            f"Most discussed {self.category.title()} ideas right now",
            f"Actionable {self.category.title()} insights for beginners",
            f"Future of {self.category.title()} in daily life",
        ][:limit]

    def _fetch_hackernews(self, limit: int) -> List[str]:
        try:
            ids_resp = requests.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                timeout=10,
            )
            ids_resp.raise_for_status()
            story_ids = ids_resp.json()[: max(limit * 2, 20)]
            topics: List[str] = []
            for sid in story_ids:
                item_resp = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=10,
                )
                if item_resp.status_code != 200:
                    continue
                data = item_resp.json() or {}
                title = data.get("title")
                if title:
                    topics.append(title)
                if len(topics) >= limit:
                    break
            return topics
        except requests.RequestException:
            return []


class ScriptGenerator:
    """Generate scripts using OpenAI or Gemini, with local fallback."""

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    def generate_script(self, topic: str, duration_seconds: int = 45) -> ScriptResult:
        prompt = (
            "Create an engaging YouTube short video script. "
            f"Topic: {topic}. "
            f"Target duration: {duration_seconds} seconds. "
            "Return plain text only with a hook, 3-4 key points, and a strong ending call-to-action. "
            "Keep language simple and energetic."
        )

        script = ""
        if self.openai_api_key:
            script = self._generate_openai(prompt)
        elif self.gemini_api_key:
            script = self._generate_gemini(prompt)

        if not script:
            script = self._fallback_script(topic)

        return ScriptResult(topic=topic, script=script.strip())

    def _generate_openai(self, prompt: str) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert short video script writer."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
            )
            return response.choices[0].message.content or ""
        except Exception:
            return ""

    def _generate_gemini(self, prompt: str) -> str:
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return (response.text or "").strip()
        except Exception:
            return ""

    @staticmethod
    def _fallback_script(topic: str) -> str:
        return (
            f"Stop scrolling! Here's why {topic} is exploding right now. "
            "First, major breakthroughs are making this topic more practical than ever. "
            "Second, creators and companies are rapidly adopting new tools and strategies. "
            "Third, people who learn this now gain a huge advantage for future opportunities. "
            "If you want to stay ahead, start with one small action today and build momentum. "
            "Follow for more quick insights!"
        )
