from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str  
    collection_name: str     
    client_id : str
    api_key : str
    checksum_key : str
    AWS_ACCESS_KEY_ID : str
    AWS_SECRET_ACCESS_KEY  : str
    AWS_DEFAULT_REGION : str
    QDRANT_URL : str
    

    class Config:
        env_file = ".env"

settings = Settings()
