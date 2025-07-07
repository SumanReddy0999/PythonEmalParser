from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    EMAIL_ADDRESS: str
    APP_PASSWORD: str
    serper_api_key: str
    openai_api_key: str
    model: str = "gpt-4o-mini"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./email_orchestrator.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
