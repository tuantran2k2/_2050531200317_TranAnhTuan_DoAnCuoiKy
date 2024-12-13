from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str  # Thêm biến này
    collection_name: str  # Thêm biến này
    qdrant_server: str    # Thêm biến này
    client_id : str
    api_key : str
    checksum_key : str
    

    class Config:
        env_file = ".env"

settings = Settings()
