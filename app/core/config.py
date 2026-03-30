from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

# Cargar .env desde la raiz del proyecto para evitar diferencias por directorio de ejecucion.
load_dotenv(dotenv_path=ENV_FILE)

class Settings(BaseSettings):
    # Valores por defecto mínimos para permitir importación en entornos de desarrollo
    DATABASE_URL_DB: str = "sqlite:///./test.db"
    SECRET_KEY: str = "dev-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM: str = ""

    PASSWORD_RESET_URL: str = "http://localhost:5173/reset-password"
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    COOKIE_SECURE: bool = False

    # Comma-separated user logins/emails that bypass module permission checks.
    PERMISSIONS_BYPASS_USERS: str = ""

    model_config = ConfigDict(env_file=str(ENV_FILE))


# Crear una instancia de Settings
settings = Settings()
