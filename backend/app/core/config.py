from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Voice Assistant"
    host: str = "127.0.0.1"
    port: int = 8787
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_voice: str = "alloy"
    data_dir: Path = Path.home() / ".ai_voice_assistant"
    max_history_messages: int = 20
    search_provider: str = "duckduckgo"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "exports").mkdir(exist_ok=True)
        (self.data_dir / "audio").mkdir(exist_ok=True)

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
