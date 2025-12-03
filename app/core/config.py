from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

load_dotenv()

class Settings(BaseSettings):
    # Valores por defecto mínimos para permitir importación en entornos de desarrollo
    DATABASE_URL_DB: str = "sqlite:///./test.db"
    SECRET_KEY: str = "dev-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = ConfigDict(env_file=".env")


# Crear una instancia de Settings
settings = Settings()
