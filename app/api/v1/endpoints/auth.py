from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import (
    authenticate_user,
    create_2fa_temp_token,
    create_access_token,
    create_password_reset_token,
    get_current_user,
    verify_2fa_temp_token,
)
from app.core.totp import (
    build_otpauth_uri,
    generate_backup_codes,
    generate_qr_svg_data_uri,
    generate_totp_secret,
    verify_and_consume_backup_code,
    verify_totp_code,
)
from app.db.session import get_db
from app.models.usuario import User
from app.schemas.user import (
    ChangePasswordRequest,
    PasswordResetRequest,
    ProfileUpdateRequest,
    TokenWithUser,
    TwoFactorDisableRequest,
    TwoFactorEnableResponse,
    TwoFactorLoginRequest,
    TwoFactorSetupRequest,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
    UserCreate,
    UserRead,
)
from app.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _verify_user_2fa_or_backup(db: Session, user: User, raw_code: str) -> bool:
    """Verifica un código TOTP de 6 dígitos o consume un código de respaldo de un solo uso."""
    code = (raw_code or "").strip()
    if not code or not user.two_factor_secret:
        return False

    if verify_totp_code(user.two_factor_secret, code):
        return True

    ok_backup, updated_json = verify_and_consume_backup_code(user.two_factor_backup_codes, code)
    if ok_backup:
        user.two_factor_backup_codes = updated_json
        db.add(user)
        db.commit()
        db.refresh(user)
        return True

    return False


@router.post(
    "/login",
    response_model=TokenWithUser,
    summary="Iniciar sesión (formulario)",
    description="Inicia sesión mediante formulario OAuth2 password. Si el usuario tiene 2FA activo, devuelve `requires_2fa=true` y `temp_token`.",
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    otp_code: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    response: Response = None,
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.id_usuario == user.id_usuario)
        .first()
    )

    if getattr(user, "two_factor_enabled", False) and getattr(user, "two_factor_secret", None):
        if otp_code:
            if not _verify_user_2fa_or_backup(db, user, otp_code):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Código de verificación 2FA inválido o expirado.",
                )
        else:
            temp_token = create_2fa_temp_token(user.login, user.id_usuario)
            return {
                "access_token": "",
                "token_type": "2fa_pending",
                "user": None,
                "requires_2fa": True,
                "temp_token": temp_token,
            }

    access_token = create_access_token(
        {"sub": user.login},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
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
        "user": user.to_dict(),
        "requires_2fa": False,
        "temp_token": None,
    }


@router.post(
    "/login/2fa",
    response_model=TokenWithUser,
    summary="Verificar segundo factor (2FA) en el inicio de sesión",
    description="Valida el `temp_token` y el código TOTP (o código de respaldo) para emitir el token de sesión definitivo.",
)
def verify_login_2fa(
    payload: TwoFactorLoginRequest,
    db: Session = Depends(get_db),
    response: Response = None,
):
    username = verify_2fa_temp_token(payload.temp_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión de verificación 2FA expiró. Por favor vuelve a ingresar tus credenciales.",
        )

    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.login == username.lower())
        .first()
    )
    if not user or not getattr(user, "activo", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no disponible o inactivo.",
        )

    if not getattr(user, "two_factor_enabled", False) or not getattr(user, "two_factor_secret", None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene 2FA configurado.",
        )

    if not _verify_user_2fa_or_backup(db, user, payload.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de verificación 2FA incorrecto. Inténtalo nuevamente.",
        )

    access_token = create_access_token(
        {"sub": user.login},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
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
        "user": user.to_dict(),
        "requires_2fa": False,
        "temp_token": None,
    }


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary="Registrar usuario",
    description="Registra un nuevo usuario. Campos: `login`, `nombre`, `correo`, `password`.",
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


@router.get(
    "/me",
    response_model=UserRead,
    summary="Información del usuario autenticado",
    description="Devuelve los datos del usuario autenticado incluyendo sus permisos de seguridad y estado de 2FA.",
)
def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.id_usuario == current_user.id_usuario)
        .first()
    )
    return user.to_dict()


@router.put(
    "/me",
    response_model=UserRead,
    summary="Actualizar mi perfil personal",
    description="Permite al usuario autenticado actualizar sus datos personales (nombre, correo, teléfono, RUT).",
)
def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.id_usuario == current_user.id_usuario)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    correo_clean = str(payload.correo).strip().lower()
    existing_email = (
        db.query(User)
        .filter(User.correo == correo_clean, User.id_usuario != user.id_usuario)
        .first()
    )
    if existing_email:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está en uso por otro usuario.")

    rut_clean = (payload.rut or "").strip()
    if rut_clean:
        existing_rut = (
            db.query(User)
            .filter(User.rut == rut_clean, User.id_usuario != user.id_usuario)
            .first()
        )
        if existing_rut:
            raise HTTPException(status_code=400, detail="El RUT ingresado ya está registrado en otra cuenta.")

    user.nombre = payload.nombre.strip()
    user.correo = correo_clean
    user.telefono = (payload.telefono or "").strip() or None
    user.rut = rut_clean or None

    db.add(user)
    db.commit()
    db.refresh(user)
    return user.to_dict()


@router.post(
    "/change-password",
    summary="Cambiar contraseña del usuario autenticado",
    description="Verifica la contraseña actual y actualiza la contraseña del usuario en sesión.",
)
def change_my_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id_usuario == current_user.id_usuario).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if not user.check_password(payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual ingresada es incorrecta.",
        )

    new_pwd = (payload.new_password or "").strip()
    if len(new_pwd) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe tener al menos 6 caracteres.",
        )

    if payload.confirm_password is not None and payload.confirm_password != new_pwd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La confirmación de contraseña no coincide.",
        )

    if user.check_password(new_pwd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la contraseña actual.",
        )

    user.set_password(new_pwd)
    db.add(user)
    db.commit()
    return {"ok": True, "message": "Contraseña actualizada exitosamente."}


@router.post(
    "/2fa/setup",
    response_model=TwoFactorSetupResponse,
    summary="Iniciar configuración de 2FA (TOTP)",
    description="Verifica la contraseña actual y genera el secreto TOTP junto con el código QR para escanear en Google/Microsoft Authenticator.",
)
def setup_two_factor(
    payload: TwoFactorSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id_usuario == current_user.id_usuario).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if not user.check_password(payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta.",
        )

    secret = generate_totp_secret()
    user.two_factor_secret = secret
    db.add(user)
    db.commit()

    issuer = "Pacific Forest Internacional"
    account = user.correo or user.login
    otpauth_uri = build_otpauth_uri(secret=secret, account_name=account, issuer=issuer)
    qr_code = generate_qr_svg_data_uri(otpauth_uri)

    return {
        "secret": secret,
        "otpauth_uri": otpauth_uri,
        "qr_code": qr_code,
        "issuer": issuer,
        "account": account,
    }


@router.post(
    "/2fa/enable",
    response_model=TwoFactorEnableResponse,
    summary="Confirmar y activar 2FA (TOTP)",
    description="Valida el código de 6 dígitos generado por la app autenticadora, activa 2FA y entrega 8 códigos de respaldo de un solo uso.",
)
def enable_two_factor(
    payload: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.id_usuario == current_user.id_usuario)
        .first()
    )
    if not user or not user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primero debes iniciar la configuración de 2FA para generar tu código QR.",
        )

    if not verify_totp_code(user.two_factor_secret, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de 6 dígitos es inválido. Verifica la hora de tu dispositivo e inténtalo de nuevo.",
        )

    plain_codes, hashed_codes_json = generate_backup_codes(8)
    user.two_factor_enabled = True
    user.two_factor_backup_codes = hashed_codes_json
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "enabled": True,
        "backup_codes": plain_codes,
        "user": user.to_dict(),
    }


@router.post(
    "/2fa/disable",
    summary="Desactivar 2FA",
    description="Desactiva la autenticación de dos factores previa validación de contraseña actual y código 2FA.",
)
def disable_two_factor(
    payload: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.id_usuario == current_user.id_usuario)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    if not user.check_password(payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta.",
        )

    if getattr(user, "two_factor_enabled", False) and payload.code:
        if not _verify_user_2fa_or_backup(db, user, payload.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código 2FA o código de respaldo ingresado es inválido.",
            )

    user.two_factor_enabled = False
    user.two_factor_secret = None
    user.two_factor_backup_codes = None
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "enabled": False,
        "message": "La autenticación de dos factores (2FA) ha sido desactivada.",
        "user": user.to_dict(),
    }


@router.post(
    "/2fa/backup-codes/regenerate",
    summary="Regenerar códigos de respaldo 2FA",
    description="Genera 8 nuevos códigos de respaldo invalidando los anteriores (requiere contraseña actual + código TOTP).",
)
def regenerate_two_factor_backup_codes(
    payload: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.id_usuario == current_user.id_usuario)
        .first()
    )
    if not user or not getattr(user, "two_factor_enabled", False) or not user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA no está activo en tu cuenta.",
        )

    if not user.check_password(payload.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta.",
        )

    if not payload.code or not verify_totp_code(user.two_factor_secret, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes ingresar un código válido de 6 dígitos de tu app autenticadora.",
        )

    plain_codes, hashed_codes_json = generate_backup_codes(8)
    user.two_factor_backup_codes = hashed_codes_json
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "backup_codes": plain_codes,
        "user": user.to_dict(),
    }


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

    # Importante: no revelar si el usuario existe o no
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
