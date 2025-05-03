from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "redis"
    redis_port: int = 6379
    app_name: str = "Scraper API"

    class Config:
        env_file = ".env"

settings = Settings()
