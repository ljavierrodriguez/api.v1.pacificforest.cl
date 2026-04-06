from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from typing import Any, Dict, List
from sqlalchemy.orm import Session, joinedload
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.models.seguridad import Seguridad
from app.models.usuario import User
from app.schemas.user import UserCreate, UserRead, UserUpdate, PasswordResetConfirm
from app.schemas.pagination import create_paginated_response, create_paginated_response_model
from app.core.security import create_password_reset_token, verify_password_reset_token
from app.core.config import settings
from app.dependencies.permissions import require_permission
from app.services.email import send_email

# Crear el modelo de respuesta paginada para Usuario
PaginatedUserResponse = create_paginated_response_model(UserRead)

router = APIRouter(prefix="/usuario", tags=["usuario"])


def _normalize_permission_entry(modulo: str, values: Dict[str, Any]) -> Dict[str, Any] | None:
    modulo_clean = str(modulo or "").strip()
    if not modulo_clean:
        return None

    return {
        "modulo": modulo_clean,
        "crear": bool(values.get("crear", values.get("create", False))),
        "ver": bool(values.get("ver", values.get("read", False))),
        "editar": bool(values.get("editar", values.get("update", False))),
        "eliminar": bool(values.get("eliminar", values.get("delete", False))),
    }


def _extract_seguridades_from_payload(payload: Any) -> List[Dict[str, Any]]:
    normalized: Dict[str, Dict[str, Any]] = {}

    for seg in getattr(payload, "seguridades", []) or []:
        item = _normalize_permission_entry(
            getattr(seg, "modulo", ""),
            {
                "crear": getattr(seg, "crear", False),
                "ver": getattr(seg, "ver", False),
                "editar": getattr(seg, "editar", False),
                "eliminar": getattr(seg, "eliminar", False),
            },
        )
        if item:
            normalized[item["modulo"].lower()] = item

    for map_name in ("permisos", "permissions"):
        permission_map = getattr(payload, map_name, None) or {}
        for modulo, values in permission_map.items():
            if not isinstance(values, dict):
                continue
            item = _normalize_permission_entry(modulo, values)
            if item:
                normalized[item["modulo"].lower()] = item

    return list(normalized.values())


@router.post(
    "/",
    response_model=UserRead,
    summary='Crear usuario',
    description='Crear un nuevo usuario.',
    dependencies=[Depends(require_permission("usuario", "create"))],
)
def create_usuario(payload: UserCreate, db: Session = Depends(get_db)):
    # Normalizar login a minúsculas para hacerlo case-insensitive
    login_lower = payload.login.lower() if payload.login else ""
    
    # Validar unicidad de rut, login y correo
    if db.query(User).filter(User.rut == payload.rut).first():
        raise HTTPException(status_code=400, detail="El RUT ya está registrado")
    if db.query(User).filter(User.login == login_lower).first():
        raise HTTPException(status_code=400, detail="El login ya existe")
    if db.query(User).filter(User.correo == str(payload.correo)).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user = User(
        rut=payload.rut,
        login=login_lower,
        nombre=payload.nombre,
        correo=str(payload.correo),
        telefono=payload.telefono,
        url_firma=payload.url_firma,
    )
    user.set_password(payload.password)
    db.add(user)
    db.flush()

    for seguridad_data in _extract_seguridades_from_payload(payload):
        db.add(Seguridad(id_usuario=user.id_usuario, **seguridad_data))

    db.commit()
    user = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == user.id_usuario).first()

    return user.to_dict()


@router.get(
    "/",
    response_model=PaginatedUserResponse,
    summary='Listar usuarios',
    description='Lista paginada de usuarios',
    dependencies=[Depends(require_permission("usuario", "read"))],
)
def list_usuarios(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(User).count()
    
    # Obtener elementos de la página actual con las relaciones cargadas
    items = db.query(User).options(joinedload(User.seguridades)).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response([u.to_dict() for u in items], page, page_size, total_items)



@router.get(
    "/{item_id}",
    response_model=UserRead,
    summary="Obtener usuario",
    description="Obtener usuario por `id_usuario`",
    dependencies=[Depends(require_permission("usuario", "read"))],
)
def get_usuario(item_id: int, db: Session = Depends(get_db)):
    item = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return item.to_dict()



@router.put(
    "/{item_id}",
    response_model=UserRead,
    summary='Actualizar usuario',
    description='Actualiza los campos del usuario (parcial).',
    dependencies=[Depends(require_permission("usuario", "update"))],
)
def update_usuario(
    item_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    item = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    old_correo = item.correo
    correo_changed = False

    # Manejar cambios sensibles
    if "rut" in data and data["rut"] != item.rut:
        if db.query(User).filter(User.rut == data["rut"]).first():
            raise HTTPException(status_code=400, detail="El RUT ya está registrado")
        item.rut = data["rut"]

    if "login" in data and data["login"] != item.login:
        # Normalizar login a minúsculas
        login_lower = data["login"].lower() if data["login"] else ""
        if db.query(User).filter(User.login == login_lower).first():
            raise HTTPException(status_code=400, detail="El login ya existe")
        item.login = login_lower

    if "correo" in data and str(data["correo"]) != item.correo:
        if db.query(User).filter(User.correo == str(data["correo"]) ).first():
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        item.correo = str(data["correo"])
        correo_changed = True

    if "password" in data:
        raise HTTPException(status_code=400, detail="Para cambiar la contraseña use el endpoint de restablecimiento")

    # Campos directos
    for field in ("nombre", "telefono", "activo", "url_firma"):
        if field in data:
            setattr(item, field, data[field])

    if any(key in data for key in ("seguridades", "permisos", "permissions")):
        item.seguridades = [
            Seguridad(id_usuario=item.id_usuario, **seguridad_data)
            for seguridad_data in _extract_seguridades_from_payload(payload)
        ]

    db.add(item)
    db.commit()
    db.refresh(item)

    if correo_changed:
        subject = "Cambio de correo"
        body_old = (
            f"Hola {item.nombre},\n\n"
            f"Tu correo de acceso fue cambiado de {old_correo} a {item.correo}.\n"
            "Si no reconoces este cambio, contacta al administrador.\n"
        )
        body_new = (
            f"Hola {item.nombre},\n\n"
            f"Este correo fue registrado como nuevo correo de acceso para tu usuario.\n"
            f"Correo anterior: {old_correo}\n"
        )

        if background_tasks:
            background_tasks.add_task(send_email, old_correo, subject, body_old)
            background_tasks.add_task(send_email, item.correo, subject, body_new)
        else:
            send_email(old_correo, subject, body_old)
            send_email(item.correo, subject, body_new)

    return item.to_dict()


@router.post(
    "/{item_id}/reset-password",
    summary="Restablecer contraseña",
    description="Envía un link de restablecimiento al correo del usuario.",
    dependencies=[Depends(require_permission("usuario", "update"))],
)
def reset_usuario_password(
    item_id: int,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    item = db.query(User).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    token = create_password_reset_token(item.id_usuario)
    separator = "&" if "?" in settings.PASSWORD_RESET_URL else "?"
    reset_url = f"{settings.PASSWORD_RESET_URL}{separator}token={token}"

    subject = "Restablecer contraseña"
    body = (
        f"Hola {item.nombre},\n\n"
        "Se solicito un restablecimiento de contraseña.\n"
        f"Puedes crear una nueva contraseña en el siguiente link:\n{reset_url}\n\n"
        "Si no solicitaste este cambio, ignora este correo.\n"
    )

    if background_tasks:
        background_tasks.add_task(send_email, item.correo, subject, body)
    else:
        send_email(item.correo, subject, body)

    return {"ok": True}


@router.post("/reset-password/confirm", summary="Confirmar restablecimiento", description="Confirma un restablecimiento de contraseña con token.")
def confirm_reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    user_id = verify_password_reset_token(payload.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Token invalido o expirado")

    item = db.query(User).filter(User.id_usuario == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    item.set_password(payload.new_password)
    db.add(item)
    db.commit()
    db.refresh(item)

    return {"ok": True}


@router.post(
    "/{item_id}/firma",
    summary='Subir firma del usuario',
    description='Sube una imagen de firma para el usuario.',
    dependencies=[Depends(require_permission("usuario", "update"))],
)
def upload_firma(item_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verificar que el usuario existe
    item = db.query(User).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Validar que sea una imagen
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Crear directorio si no existe
    upload_dir = os.path.join(os.getcwd(), "app", "static", "firmas")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"firma_{item_id}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Guardar el archivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    
    # Actualizar la URL en la base de datos
    url_firma = f"/static/firmas/{filename}"
    item.url_firma = url_firma
    db.commit()
    db.refresh(item)
    
    return {"url_firma": url_firma, "message": "Firma subida exitosamente"}


@router.delete(
    "/{item_id}",
    summary='Eliminar usuario',
    description='Elimina un usuario por `id_usuario`.',
    dependencies=[Depends(require_permission("usuario", "delete"))],
)
def delete_usuario(item_id: int, db: Session = Depends(get_db)):
    item = db.get(User, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}
