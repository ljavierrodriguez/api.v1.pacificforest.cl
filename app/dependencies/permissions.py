from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.usuario import (
    MANTENEDOR_MODULES,
    SYSTEM_MODULES,
    User,
    normalize_module_code,
)

_ACTION_TO_COLUMN = {
    "create": "crear",
    "crear": "crear",
    "read": "ver",
    "ver": "ver",
    "update": "editar",
    "editar": "editar",
    "delete": "eliminar",
    "eliminar": "eliminar",
}

_METHOD_TO_ACTION = {
    "GET": "read",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}

# Módulos relacionados que permiten lectura cruzada (GET) cuando un flujo operativo depende de ellos
_RELATED_READ_MODULES = {
    "EXPORTACION": ("PROFORMA",),
    "PROFORMA": ("EXPORTACION", "ORDEN_COMPRA"),
    "ORDEN_COMPRA": (
        "PROFORMA",
        "INVENTARIO_TRANSITORIO",
        "INVENTARIO_PUERTO",
        "ORDEN_SERVICIO",
        "GUIA_COSTO_SERVICIO",
    ),
    "INVENTARIO_DASHBOARD": (
        "INVENTARIO_TRANSITORIO",
        "INVENTARIO_PUERTO",
        "INVENTARIO_SEGUNDA",
    ),
    "INVENTARIO_TRANSITORIO": (
        "INVENTARIO_DASHBOARD",
        "INVENTARIO_PUERTO",
        "ORDEN_SERVICIO",
        "GUIA_COSTO_SERVICIO",
    ),
    "INVENTARIO_PUERTO": ("INVENTARIO_DASHBOARD", "EXPORTACION"),
    "INVENTARIO_SEGUNDA": ("INVENTARIO_DASHBOARD", "GUIA_COSTO_SERVICIO", "SERVICIOS_DASHBOARD"),
    "ORDEN_SERVICIO": ("SERVICIOS_DASHBOARD", "INVENTARIO_PUERTO", "GUIA_COSTO_SERVICIO", "INVENTARIO_TRANSITORIO"),
    "GUIA_COSTO_SERVICIO": ("SERVICIOS_DASHBOARD", "INVENTARIO_PUERTO", "INVENTARIO_SEGUNDA", "ORDEN_SERVICIO"),
}


def _is_bypass_user(user: User) -> bool:
    if user.is_admin_user():
        return True
    bypass_raw = getattr(settings, "PERMISSIONS_BYPASS_USERS", "") or ""
    bypass_set = {u.strip().lower() for u in bypass_raw.split(",") if u.strip()}
    if not bypass_set:
        return False
    return (user.login or "").strip().lower() in bypass_set or (user.correo or "").strip().lower() in bypass_set


def _check_permission(db: Session, user: User, modulo: str, action: str) -> None:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    if not getattr(user, "activo", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo. Contacte al administrador.")

    if _is_bypass_user(user):
        return None

    perm_column = _ACTION_TO_COLUMN.get((action or "").strip().lower())
    if not perm_column:
        return None

    canonical_mod = normalize_module_code(modulo)

    # Asegurar que seguridades están cargadas
    if user.seguridades is None:
        user = (
            db.query(User)
            .options(joinedload(User.seguridades))
            .filter(User.id_usuario == user.id_usuario)
            .first()
        ) or user

    user_dict = user.to_dict()
    if user_dict.get("rol") == "ADMINISTRADOR":
        return None

    permisos_map = user_dict.get("permisos", {})
    mod_perms = permisos_map.get(canonical_mod, {})

    if mod_perms.get(perm_column, False):
        return None

    # Para lecturas (GET):
    if perm_column == "ver":
        # 1. Permitir lectura de catálogos/mantenedores y listado de usuarios encargados
        # si el usuario tiene acceso de lectura a cualquier módulo del sistema
        if canonical_mod in MANTENEDOR_MODULES or canonical_mod == "USUARIO":
            has_any_access = any(
                permisos_map.get(m, {}).get("ver", False) for m in SYSTEM_MODULES
            )
            if has_any_access:
                return None

        # 2. Permitir lectura cruzada entre módulos operativos estrechamente vinculados
        for related_mod in _RELATED_READ_MODULES.get(canonical_mod, ()):
            if permisos_map.get(related_mod, {}).get("ver", False):
                return None

    action_labels = {
        "ver": "visualizar",
        "crear": "crear registros en",
        "editar": "editar registros en",
        "eliminar": "eliminar registros en",
    }
    verb = action_labels.get(perm_column, "acceder a")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"No tienes permisos para {verb} el módulo '{canonical_mod}'.",
    )


def require_permission(modulo: str, action: str):
    action_key = (action or "").strip().lower()
    modulo_key = (modulo or "").strip().upper()

    def _dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        _check_permission(db, current_user, modulo_key, action_key)
        return current_user

    return _dependency


def require_module_access(modulo: str):
    modulo_key = (modulo or "").strip().upper()

    def _dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        action = _METHOD_TO_ACTION.get(request.method.upper())
        if action is None:
            return current_user

        _check_permission(db, current_user, modulo_key, action)
        return current_user

    return _dependency
