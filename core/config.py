from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    environment: str = "development"
    max_tokens: int = 150

    class Config:
        env_file = ".env"  # Load variables from this file automatically

settings = Settings()
