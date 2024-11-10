from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str  # Thêm biến này
    collection_name: str  # Thêm biến này
    qdrant_server: str    # Thêm biến này

    class Config:
        env_file = ".env"

settings = Settings()
