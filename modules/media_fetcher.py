"""Fetch stock images/videos from free providers or generate local placeholders."""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import List

import requests
from PIL import Image, ImageDraw, ImageFont


class MediaFetcher:
    def __init__(self, output_dir: str = "temp/media") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pexels_api_key = os.getenv("PEXELS_API_KEY", "")
        self.unsplash_api_key = os.getenv("UNSPLASH_ACCESS_KEY", "")

    def fetch_images(self, query: str, count: int = 6) -> List[str]:
        images = self._from_pexels(query, count)
        if len(images) < count:
            images.extend(self._from_unsplash(query, count - len(images)))

        if len(images) < count:
            images.extend(self._placeholder_images(query, count - len(images)))

        return images[:count]

    def _from_pexels(self, query: str, count: int) -> List[str]:
        if not self.pexels_api_key:
            return []

        headers = {"Authorization": self.pexels_api_key}
        params = {"query": query, "per_page": count, "orientation": "portrait"}
        try:
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            files: List[str] = []
            for idx, photo in enumerate(data.get("photos", []), start=1):
                img_url = photo.get("src", {}).get("large2x")
                if not img_url:
                    continue
                file_path = self.output_dir / f"pexels_{idx}.jpg"
                self._download(img_url, file_path)
                files.append(str(file_path))
            return files
        except requests.RequestException:
            return []

    def _from_unsplash(self, query: str, count: int) -> List[str]:
        if not self.unsplash_api_key:
            return []

        params = {"query": query, "per_page": count, "orientation": "portrait"}
        headers = {"Authorization": f"Client-ID {self.unsplash_api_key}"}
        try:
            response = requests.get(
                "https://api.unsplash.com/search/photos",
                headers=headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            files: List[str] = []
            for idx, item in enumerate(data.get("results", []), start=1):
                img_url = item.get("urls", {}).get("regular")
                if not img_url:
                    continue
                file_path = self.output_dir / f"unsplash_{idx}.jpg"
                self._download(img_url, file_path)
                files.append(str(file_path))
            return files
        except requests.RequestException:
            return []

    @staticmethod
    def _download(url: str, destination: Path) -> None:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        destination.write_bytes(resp.content)

    def _placeholder_images(self, query: str, count: int) -> List[str]:
        files: List[str] = []
        for idx in range(count):
            color = (
                random.randint(10, 50),
                random.randint(60, 120),
                random.randint(140, 240),
            )
            image = Image.new("RGB", (1080, 1920), color)
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            text = f"{query}\nAuto-generated visual {idx + 1}"
            draw.multiline_text((80, 140), text, fill=(255, 255, 255), font=font, spacing=8)
            out = self.output_dir / f"placeholder_{idx + 1}.jpg"
            image.save(out)
            files.append(str(out))
        return files
