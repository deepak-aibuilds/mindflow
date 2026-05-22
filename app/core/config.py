from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    mistral_api_key: str
    groq_api_key: str = ""
    secret_key: str = ''
    supabase_url: str
    supabase_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()