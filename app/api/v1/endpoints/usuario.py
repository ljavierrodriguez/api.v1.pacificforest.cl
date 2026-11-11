from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.dependencies.permissions import require_module_access, require_permission
from app.models.seguridad import Seguridad
from app.models.usuario import (
    ROLE_TEMPLATES,
    SYSTEM_MODULES_CATALOG,
    User,
    normalize_module_code,
)
from app.schemas.user import UserCreate, UserRead, UserUpdate, PasswordResetConfirm
from app.schemas.pagination import create_paginated_response, create_paginated_response_model
from app.core.security import create_password_reset_token, verify_password_reset_token
from app.core.config import settings
from app.services.email import send_email

# Crear el modelo de respuesta paginada para Usuario
PaginatedUserResponse = create_paginated_response_model(UserRead)

router = APIRouter(prefix="/usuario", tags=["usuario"])


def _normalize_permission_entry(modulo: str, values: Dict[str, Any]) -> Dict[str, Any] | None:
    modulo_clean = normalize_module_code(str(modulo or ""))
    if not modulo_clean:
        return None

    crear = bool(values.get("crear", values.get("create", False)))
    editar = bool(values.get("editar", values.get("update", False)))
    eliminar = bool(values.get("eliminar", values.get("delete", False)))
    ver = bool(values.get("ver", values.get("read", False))) or crear or editar or eliminar

    return {
        "modulo": modulo_clean[:60],
        "crear": crear,
        "ver": ver,
        "editar": editar,
        "eliminar": eliminar,
    }


def _extract_seguridades_from_payload(payload: Any, rol: Optional[str] = None) -> List[Dict[str, Any]]:
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
            normalized[item["modulo"]] = item

    for map_name in ("permisos", "permissions"):
        permission_map = getattr(payload, map_name, None) or {}
        for modulo, values in permission_map.items():
            if not isinstance(values, dict):
                continue
            item = _normalize_permission_entry(modulo, values)
            if item:
                normalized[item["modulo"]] = item

    # Si no se enviaron permisos explícitos y el rol tiene plantilla predefinida, usar plantilla
    rol_key = (rol or getattr(payload, "rol", "") or "").strip().upper()
    if not normalized and rol_key in ROLE_TEMPLATES:
        for mod_code, perms in ROLE_TEMPLATES[rol_key]["permisos"].items():
            item = _normalize_permission_entry(mod_code, perms)
            if item:
                normalized[item["modulo"]] = item

    # Si el rol es ADMINISTRADOR, garantizar que todos los módulos tengan control total
    if rol_key == "ADMINISTRADOR":
        for mod_code, perms in ROLE_TEMPLATES["ADMINISTRADOR"]["permisos"].items():
            item = _normalize_permission_entry(mod_code, perms)
            if item:
                normalized[item["modulo"]] = item

    return list(normalized.values())


@router.get(
    "/catalogo-permisos",
    summary="Catálogo de módulos y plantillas de roles",
    description="Devuelve la lista oficial de módulos del sistema agrupados por categoría y las plantillas de roles disponibles.",
)
def get_catalogo_permisos(
    _current_user: User = Depends(require_module_access("USUARIO")),
):
    return {
        "modulos": SYSTEM_MODULES_CATALOG,
        "roles": list(ROLE_TEMPLATES.values()),
    }


@router.post(
    "/",
    response_model=UserRead,
    summary="Crear usuario",
    description="Crear un nuevo usuario con su rol y matriz de permisos.",
)
def create_usuario(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_permission("USUARIO", "create")),
):
    login_lower = payload.login.strip().lower() if payload.login else ""
    rut_clean = (payload.rut or "").strip()
    rol_clean = (payload.rol or "PERSONALIZADO").strip().upper()
    if rol_clean not in ROLE_TEMPLATES:
        rol_clean = "PERSONALIZADO"

    # Validar unicidad de rut, login y correo
    if rut_clean and db.query(User).filter(User.rut == rut_clean).first():
        raise HTTPException(status_code=400, detail="El RUT ya está registrado")
    if db.query(User).filter(User.login == login_lower).first():
        raise HTTPException(status_code=400, detail="El login ya existe")
    if db.query(User).filter(User.correo == str(payload.correo).strip()).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user = User(
        rut=rut_clean or None,
        login=login_lower,
        nombre=payload.nombre.strip(),
        correo=str(payload.correo).strip(),
        telefono=(payload.telefono or "").strip(),
        url_firma=payload.url_firma,
        rol=rol_clean,
        activo=payload.activo if payload.activo is not None else True,
    )
    user.set_password(payload.password)
    db.add(user)
    db.flush()

    for seguridad_data in _extract_seguridades_from_payload(payload, rol=rol_clean):
        db.add(Seguridad(id_usuario=user.id_usuario, **seguridad_data))

    db.commit()
    user = (
        db.query(User)
        .options(joinedload(User.seguridades))
        .filter(User.id_usuario == user.id_usuario)
        .first()
    )

    return user.to_dict()


@router.get(
    "/",
    response_model=PaginatedUserResponse,
    summary="Listar usuarios",
    description="Lista paginada de usuarios",
)
def list_usuarios(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=1000, description="Tamaño de página"),
    search: str = Query(None, description="Término de búsqueda"),
    rol: Optional[str] = Query(None, description="Filtrar por rol"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_module_access("USUARIO")),
):
    skip = (page - 1) * page_size
    query = db.query(User)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.nombre.ilike(search_pattern),
                User.login.ilike(search_pattern),
                User.correo.ilike(search_pattern),
                User.rut.ilike(search_pattern),
                User.rol.ilike(search_pattern),
            )
        )

    if rol and rol.strip():
        query = query.filter(User.rol == rol.strip().upper())

    if activo is not None:
        query = query.filter(User.activo == activo)

    total_items = query.count()
    items = (
        query.order_by(User.id_usuario.asc())
        .options(joinedload(User.seguridades))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    return create_paginated_response([u.to_dict() for u in items], page, page_size, total_items)


@router.get(
    "/{item_id}",
    response_model=UserRead,
    summary="Obtener usuario",
    description="Obtener usuario por `id_usuario`",
)
def get_usuario(
    item_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_module_access("USUARIO")),
):
    item = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return item.to_dict()


@router.put(
    "/{item_id}",
    response_model=UserRead,
    summary="Actualizar usuario",
    description="Actualiza los campos, rol, estado y permisos del usuario.",
)
def update_usuario(
    item_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
    _current_user: User = Depends(require_permission("USUARIO", "update")),
):
    item = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)
    old_correo = item.correo
    correo_changed = False

    # Manejar cambios sensibles
    if "rut" in data:
        new_rut = (data["rut"] or "").strip() or None
        if new_rut != item.rut:
            if new_rut and db.query(User).filter(User.rut == new_rut, User.id_usuario != item_id).first():
                raise HTTPException(status_code=400, detail="El RUT ya está registrado")
            item.rut = new_rut

    if "login" in data and data["login"]:
        login_lower = data["login"].strip().lower()
        if login_lower != item.login:
            if db.query(User).filter(User.login == login_lower, User.id_usuario != item_id).first():
                raise HTTPException(status_code=400, detail="El login ya existe")
            item.login = login_lower

    if "correo" in data and data["correo"]:
        new_correo = str(data["correo"]).strip()
        if new_correo != item.correo:
            if db.query(User).filter(User.correo == new_correo, User.id_usuario != item_id).first():
                raise HTTPException(status_code=400, detail="El correo ya está registrado")
            item.correo = new_correo
            correo_changed = True

    if "password" in data and data["password"] and str(data["password"]).strip():
        item.set_password(str(data["password"]).strip())

    if "rol" in data and data["rol"]:
        rol_clean = str(data["rol"]).strip().upper()
        item.rol = rol_clean if rol_clean in ROLE_TEMPLATES else "PERSONALIZADO"

    # Campos directos
    for field in ("nombre", "telefono", "activo", "url_firma"):
        if field in data:
            setattr(item, field, data[field])

    if any(key in data for key in ("seguridades", "permisos", "permissions")):
        seguridades_data = _extract_seguridades_from_payload(payload, rol=item.rol)
        db.query(Seguridad).filter(Seguridad.id_usuario == item.id_usuario).delete(synchronize_session=False)
        db.flush()
        for seguridad_data in seguridades_data:
            db.add(Seguridad(id_usuario=item.id_usuario, **seguridad_data))

    db.add(item)
    db.commit()
    db.expire_all()
    item = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == item_id).first()

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
            try:
                send_email(old_correo, subject, body_old)
                send_email(item.correo, subject, body_new)
            except Exception:
                pass

    return item.to_dict()


@router.post("/{item_id}/reset-password")
def reset_usuario_password(
    item_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_permission("USUARIO", "update")),
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
        "Se solicitó un restablecimiento de contraseña.\n"
        f"Puedes crear una nueva contraseña en el siguiente link:\n{reset_url}\n\n"
        "Si no solicitaste este cambio, ignora este correo.\n"
    )

    try:
        send_email(item.correo, subject, body)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando correo: {str(e)}"
        )

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
    summary="Subir firma del usuario",
    description="Sube una imagen de firma para el usuario.",
)
def upload_firma(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_permission("USUARIO", "update")),
):
    item = db.query(User).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    upload_dir = os.path.join(os.getcwd(), "app", "static", "firmas")
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"firma_{item_id}_{timestamp}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    url_firma = f"/static/firmas/{filename}"
    item.url_firma = url_firma
    db.commit()
    db.refresh(item)

    return {"url_firma": url_firma, "message": "Firma subida exitosamente"}


@router.delete(
    "/{item_id}",
    summary="Eliminar usuario",
    description="Elimina un usuario por `id_usuario`.",
)
def delete_usuario(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("USUARIO", "delete")),
):
    if current_user.id_usuario == item_id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario activo.")
    item = db.get(User, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}
