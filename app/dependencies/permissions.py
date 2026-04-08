from fastapi import Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

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


def _check_permission(db: Session, user: User, modulo: str, action: str) -> None:
    # Permisos deshabilitados temporalmente.
    # El acceso queda abierto para usuarios autenticados y la gestión visual
    # de módulos se mantiene desde la pantalla de seguridad.
    return None


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
