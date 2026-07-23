import logging
from logging.handlers import RotatingFileHandler
from .config import get_settings

def configure_logging() -> None:
    settings = get_settings()
    log_file = settings.data_dir / "assistant.log"
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logging.getLogger().addHandler(handler)
