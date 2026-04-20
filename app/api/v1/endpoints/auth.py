from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form,  BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from datetime import timedelta
from app.schemas.user import UserCreate, UserRead, Token, TokenWithUser, PasswordResetRequest
from app.schemas.pagination import create_paginated_response
from app.models.usuario import User
from app.db.session import get_db
from app.core.config import settings
from app.core.security import create_access_token, authenticate_user, get_current_user, create_password_reset_token
from app.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])

# Endpoint de inicio de sesión (formulario)
@router.post(
        "/login",
        response_model=TokenWithUser,
        summary='Iniciar sesión (formulario)',
        description=(
                """
                Inicia sesión mediante un formulario usando el flujo OAuth2 `password`.

                - Tipo de contenido: `application/x-www-form-urlencoded`.
                - Campos requeridos por el formulario:
                    - `username`: nombre de usuario
                    - `password`: contraseña

                Ejemplo `curl`:

                ```bash
                curl -X POST "http://localhost:8000/api/v1/auth/login" \
                    -H "Content-Type: application/x-www-form-urlencoded" \
                    -d "username=miusuario&password=miclave"
                ```

                Ejemplo HTML (formulario simple):

                ```html
                <form action="/api/v1/auth/login" method="post">
                    <input name="username" type="text" />
                    <input name="password" type="password" />
                    <button type="submit">Entrar</button>
                </form>
                ```

                Respuesta JSON:

                ```json
                {
                    "access_token": "<token>",
                    "token_type": "bearer",
                    "user": {
                        "id_usuario": 1,
                        "login": "miusuario",
                        "nombre": "Mi Nombre",
                        "correo": "usuario@example.com",
                        "seguridades": [
                            {
                                "id_seguridad": 1,
                                "id_usuario": 1,
                                "modulo": "proforma",
                                "crear": true,
                                "ver": true,
                                "editar": true,
                                "eliminar": false
                            }
                        ]
                    }
                }
                ```

                Nota:
                - Si la función recibe un objeto `response`, el token también se almacena en una cookie `access_token` (HttpOnly, Secure, SameSite=lax) pensada para clientes de navegador.
                - Para peticiones desde JavaScript use `FormData` o `URLSearchParams` y envíe `Content-Type: application/x-www-form-urlencoded`.
                """
        ),
)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
        response: Response = None,
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Cargar las seguridades del usuario
    user = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == user.id_usuario).first()

    
    access_token = create_access_token(
        {"sub": user.login},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    # Optionally set token in cookie for browser clients
    if response:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
        )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


# User registration endpoint
@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary='Registrar usuario',
    description='Registra un nuevo usuario. Campos: `login`, `nombre`, `correo`, `password`.',
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.login == payload.login).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        login=payload.login,
        nombre=payload.nombre,
        correo=str(payload.correo),
    )
    user.set_password(payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.to_dict()


# Protected endpoint to get current user info
@router.get(
    "/me",
    response_model=UserRead,
    summary='Información del usuario autenticado',
    description='Devuelve los datos del usuario autenticado incluyendo sus permisos de seguridad (requiere token Bearer).',
)
def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Cargar las seguridades del usuario
    user = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == current_user.id_usuario).first()
    return user.to_dict()

@router.post(
    "/reset-password",
    summary="Restablecer contraseña",
    description="Envía un link de restablecimiento al correo del usuario.",
)
def reset_usuario_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    item = db.query(User).filter(User.correo == request.email).first()

    # ⚠️ Importante: no revelar si el usuario existe o no
    if not item:
        return {"ok": True}

    token = create_password_reset_token(item.id_usuario)
    separator = "&" if "?" in settings.PASSWORD_RESET_URL else "?"
    reset_url = f"{settings.PASSWORD_RESET_URL}{separator}token={token}"

    subject = "Restablecer contraseña"
    body = (
        f"Hola {item.nombre},\n\n"
        "Se solicitó un restablecimiento de contraseña.\n"
        f"Puedes crear una nueva contraseña en el siguiente link:\n{reset_url}\n\n"
        "Si no solicitaste este cambio, ignora este correo.\n"
    )

    if background_tasks:
        background_tasks.add_task(send_email, item.correo, subject, body)
    else:
        send_email(item.correo, subject, body)

    return {"ok": True}