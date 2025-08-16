from pydantic_settings import BaseSettings,SettingsConfigDict


class Config(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    FILE_ALOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_SIZE_CHUNK: int = 1024  # Default chunk size for file uploads
    class Config:
        env_file = ".env"
        

def get_config():
    return Config()
