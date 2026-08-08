from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    app_env: str = "development"
    database_url: str = "sqlite:///./data/app.db"
    log_level: str = "INFO"
    http_timeout_seconds: float = 20
    http_max_retries: int = 3
    crawl_delay_seconds: float = 2
    crawl_max_concurrency: int = 2
    playwright_headless: bool = True
    playwright_browsers_path: str = "./data/playwright-browsers"
    enable_external_requests: bool = True
    save_page_snapshots: bool = True
    save_screenshots: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
