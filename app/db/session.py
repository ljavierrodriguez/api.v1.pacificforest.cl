from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Base de datos 1
engine_db = create_engine(settings.DATABASE_URL_DB)
SessionLocalDB = sessionmaker(autocommit=False, autoflush=False, bind=engine_db)

# Crear una función que proporcione una sesión para DB1
def get_db():
    db = SessionLocalDB()
    try:
        yield db
    finally:
        db.close()
