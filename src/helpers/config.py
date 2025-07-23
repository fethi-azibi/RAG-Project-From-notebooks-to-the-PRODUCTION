from pydantic_settings import BaseSettings, SettingConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEEPSEEK_API_KEY: str
    
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    
    class config:
        env_file = ".env"

def get_settings(self):
    return Settings()