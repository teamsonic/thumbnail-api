"""Global settings for the application, initialized and available on startup

Exports:

settings - An instance of a data class containing application configuration settings
"""

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    """Data class containing application configuration settings

    On startup, if a ".env" file is present in the current working directory,
    the value of any matching tokens in the file will overwrite the defaults.
    """

    app_name: str = "thumbnail-api"
    app_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
