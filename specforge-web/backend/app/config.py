from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    specforge_module_path: Path = Path(__file__).resolve().parents[2] / ".." / "specforge-module"
    workspace_root: Path = Path(__file__).resolve().parents[2] / "workspace"
    database_url: str = "sqlite+aiosqlite:///./specforge-web.db"
    claude_cli_path: str = "claude"
    langfuse_public_key: str = "pk-lf-local-dev"
    langfuse_secret_key: str = "sk-lf-local-dev"
    langfuse_host: str = "http://localhost:3000"
    cors_origins: str = "http://localhost:5173"
    poll_interval_seconds: int = 600

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
