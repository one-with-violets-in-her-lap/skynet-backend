from typing import Optional
import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE_PATH = os.environ.get("SKYNET__ENV_FILE") or "./.env"

logger = logging.getLogger(__name__)


class WebsocketsApiConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="SKYNET__",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8000

    proxy_url: Optional[str] = None

    cors_allowed_origins: list[str]

    @staticmethod
    def load_from_env():
        return WebsocketsApiConfig.model_validate({})


logger.info("Loading config (.env) from '%s'", ENV_FILE_PATH)
websockets_api_config = WebsocketsApiConfig.load_from_env()
