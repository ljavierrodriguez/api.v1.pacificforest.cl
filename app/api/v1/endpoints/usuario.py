from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.usuario import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/usuario", tags=["usuario"])


@router.post("/", response_model=UserRead, summary='Crear usuario', description='Crear un nuevo usuario.')
def create_usuario(payload: UserCreate, db: Session = Depends(get_db)):
    # Validar unicidad de login y correo
    if db.query(User).filter(User.login == payload.login).first():
        raise HTTPException(status_code=400, detail="El login ya existe")
    if db.query(User).filter(User.correo == str(payload.correo)).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user = User(
        login=payload.login,
        nombre=payload.nombre,
        correo=str(payload.correo),
    )
    user.set_password(payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=List[UserRead], summary='Listar usuarios', description='Lista paginada de usuarios')
def list_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(User).offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=UserRead, summary='Obtener usuario', description='Obtener usuario por `id_usuario`')
def get_usuario(item_id: int, db: Session = Depends(get_db)):
    item = db.get(User, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return item


@router.put("/{item_id}", response_model=UserRead, summary='Actualizar usuario', description='Actualiza los campos del usuario (parcial). Si se incluye `password`, será re-hasheada.')
def update_usuario(item_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    item = db.get(User, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_unset=True)

    # Manejar cambios sensibles
    if "login" in data and data["login"] != item.login:
        if db.query(User).filter(User.login == data["login"]).first():
            raise HTTPException(status_code=400, detail="El login ya existe")
        item.login = data["login"]

    if "correo" in data and str(data["correo"]) != item.correo:
        if db.query(User).filter(User.correo == str(data["correo"]) ).first():
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        item.correo = str(data["correo"])

    if "password" in data and data["password"]:
        item.set_password(data["password"])

    # Campos directos
    for field in ("nombre", "telefono", "activo"):
        if field in data:
            setattr(item, field, data[field])

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='Eliminar usuario', description='Elimina un usuario por `id_usuario`.')
def delete_usuario(item_id: int, db: Session = Depends(get_db)):
    item = db.get(User, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}
