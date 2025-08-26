from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List  # << مهم

class Config(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: List[str]  # بدل list[str]
    FILE_MAX_SIZE: int
    FILE_SIZE_CHUNK: int = 1024
    DEEPSEEK_API_KEY: str
    QWEN_API_KEY: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

def get_config():
    return Config()
