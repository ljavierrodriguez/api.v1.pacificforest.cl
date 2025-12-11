from datetime import datetime, timedelta
from typing import Optional

from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import User
from app.schemas.user import TokenData
from app.db.session import get_db
from app.core.config import settings

# Contexto para cifrar y verificar contraseñas
# Incluye bcrypt legado para poder verificar y rehashar automáticamente
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="bcrypt",
)

# URL para OAuth2 login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str):
    """Verifica la contraseña y, si es legado, devuelve un nuevo hash para rehash."""
    try:
        ok, new_hash = pwd_context.verify_and_update(plain_password, hashed_password)
        return ok, new_hash
    except ValueError as exc:
        # Maneja contraseñas >72 bytes contra hashes bcrypt legacy truncando a 72
        if "password cannot be longer than 72 bytes" in str(exc):
            truncated = (plain_password or "")[:72]
            try:
                ok, new_hash = pwd_context.verify_and_update(truncated, hashed_password)
                return ok, new_hash
            except Exception:
                return False, None
        return False, None


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.login == username).first()
    if not user:
        return False
    ok, new_hash = verify_password(password, user.hashed_password)
    if not ok:
        return False
    if new_hash:
        user.pass_ = new_hash
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.login == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_from_cookie(request) -> dict | None:
    """Helper used by the template routes to read the access token from a cookie.

    Returns a minimal dict with 'username' and optional 'role', or None if invalid.
    """
    token = None
    try:
        token = request.cookies.get("access_token")
    except Exception:
        return None

    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            return None
        return {"username": username, "role": role}
    except Exception:
        return None
