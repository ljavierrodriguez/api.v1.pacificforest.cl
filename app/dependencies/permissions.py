from fastapi import Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.seguridad import Seguridad
from app.models.usuario import User

_ACTION_TO_COLUMN = {
    "create": "crear",
    "read": "ver",
    "update": "editar",
    "delete": "eliminar",
}

_METHOD_TO_ACTION = {
    "GET": "read",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}


def _normalize_bypass_entry(value: str) -> str:
    """Normalize env entries to tolerate quotes and list-like values from hosting panels."""
    normalized = (value or "").strip().lower()
    if not normalized:
        return ""

    # Common wrappers users paste in env vars, e.g. "user", 'user', [user]
    normalized = normalized.strip("\"'")
    normalized = normalized.strip("[]")
    normalized = normalized.strip("\"'")
    return normalized


def _get_bypass_users() -> set[str]:
    raw_users = settings.PERMISSIONS_BYPASS_USERS or ""
    if not raw_users:
        return set()

    separators_normalized = raw_users.replace(";", ",").replace("\n", ",")
    users: set[str] = set()
    for item in separators_normalized.split(","):
        normalized_item = _normalize_bypass_entry(item)
        if normalized_item:
            users.add(normalized_item)
    return users


def _is_bypass_user(user: User) -> bool:
    allowed_users = _get_bypass_users()
    if not allowed_users:
        return False

    if "*" in allowed_users:
        return True

    user_login = (user.login or "").strip().lower()
    user_email = (user.correo or "").strip().lower()
    return user_login in allowed_users or user_email in allowed_users


def _check_permission(db: Session, user: User, modulo: str, action: str) -> None:
    if _is_bypass_user(user):
        return

    action_key = (action or "").strip().lower()
    if action_key not in _ACTION_TO_COLUMN:
        raise ValueError(f"Accion de permiso no soportada: {action}")

    modulo_key = (modulo or "").strip().lower()
    modulo_candidates = {modulo_key}
    if len(modulo_key) > 15:
        modulo_candidates.add(modulo_key[:15])

    permiso_columna = _ACTION_TO_COLUMN[action_key]

    permiso = (
        db.query(Seguridad)
        .filter(Seguridad.id_usuario == user.id_usuario)
        .filter(func.lower(Seguridad.modulo).in_(modulo_candidates))
        .first()
    )

    if not permiso or not bool(getattr(permiso, permiso_columna, False)):
        raise HTTPException(
            status_code=403,
            detail=f"No tienes permiso '{action_key}' para el modulo '{modulo_key}'",
        )


def require_permission(modulo: str, action: str):
    action_key = (action or "").strip().lower()
    modulo_key = (modulo or "").strip().lower()

    def _dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        _check_permission(db, current_user, modulo_key, action_key)
        return current_user

    return _dependency


def require_module_access(modulo: str):
    modulo_key = (modulo or "").strip().lower()

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
