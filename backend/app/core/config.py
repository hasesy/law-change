from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    app_name: str = "Law Change History API"
    app_env: str = "local"
    
    database_url: str

    # NLIC settings
    nlic_oc: str
    nlic_history_url: str
    nlic_oldnew_url: str
    
    # AI Settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "qwen2.5:7b-instruct"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()

