from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str = ""
    secret_key: str = "dev-secret-change-in-prod"
    database_url: str = "sqlite:///./careeraidb.sqlite"
    frontend_url: str = "http://localhost:3000"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
