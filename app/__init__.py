from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    app_name: str = "thumbnail-api"
    app_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
