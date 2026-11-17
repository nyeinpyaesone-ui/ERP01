"""Validated gateway configuration. Service URLs are deployment-owned allowlist entries."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    gateway_port: int = Field(default=8000, ge=1, le=65535)
    modules_enabled: str = "inventory,sales,core,finance"
    redis_url: str = "redis://redis:6379/0"
    request_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    health_timeout_seconds: float = Field(default=4.0, gt=0, le=15)
    enable_api_docs: bool = False

    def enabled_module_names(self) -> list[str]:
        return sorted({
            name.strip().lower()
            for name in self.modules_enabled.split(",")
            if name.strip()
        })


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
