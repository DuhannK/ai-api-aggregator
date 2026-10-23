from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    INTERNAL_API_KEY: str
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Gelecekte eklenecek özellikler için yer tutucular
    # TTS_ENABLED: bool = False
    # IMAGE_GEN_ENABLED: bool = False

    class Config:
        env_file = ".env"
        extra = 'ignore' # Bilinmeyen değişkenleri görmezden gel

settings = Settings()
