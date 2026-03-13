from dataclasses import dataclass
from pathlib import Path


@dataclass
class VideoSettings:
    topic: str
    tone: str
    duration_seconds: int
    voice_name: str
    orientation: str
    include_bgm: bool
    bgm_volume: float

    @property
    def resolution(self) -> tuple[int, int]:
        return (1080, 1920) if self.orientation == "YouTube Shorts (9:16)" else (1920, 1080)


@dataclass
class Paths:
    outputs: Path = Path("outputs")
    temp: Path = Path("outputs/temp")

    def ensure(self) -> None:
        self.outputs.mkdir(parents=True, exist_ok=True)
        self.temp.mkdir(parents=True, exist_ok=True)
