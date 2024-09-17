"""Global settings for the application, initialized and available on startup

Exports:

settings - An instance of a data class containing application configuration settings
"""

from typing import Tuple

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    """Data class containing application configuration settings

    On startup, if a ".env" file is present in the current working directory,
    the value of any matching tokens in the file will overwrite the defaults.
    """

    app_name: str = "thumbnail-api"
    app_port: int = 8000
    max_file_size: int = 1024 * 1024 * 5  # 5MB
    thumbnail_size: Tuple[int, int] = (100, 100)
    thumbnail_file_type: str = "JPEG"
    thumbnail_background: Tuple[int, int, int] = (255, 255, 255)  # White

    class Config:
        env_file = ".env"


settings = Settings()
