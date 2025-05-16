# apiserver/src/apiserver/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "my-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
