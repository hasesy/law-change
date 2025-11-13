from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Law Change History API"
    app_env: str = "local"
    database_url: str

    nlic_oc: str
    nlic_history_url: str
    nlic_oldnew_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
