from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.usuario import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Usuario
PaginatedUserResponse = create_paginated_response_model(UserRead)

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
    
    return user.to_dict()


@router.get("/", response_model=PaginatedUserResponse, summary='Listar usuarios', description='Lista paginada de usuarios')
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



@router.get("/{item_id}", response_model=UserRead, summary="Obtener usuario", description="Obtener usuario por `id_usuario`")
def get_usuario(item_id: int, db: Session = Depends(get_db)):
    item = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return item.to_dict()



@router.put("/{item_id}", response_model=UserRead, summary='Actualizar usuario', description='Actualiza los campos del usuario (parcial). Si se incluye `password`, será re-hasheada.')
def update_usuario(item_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    item = db.query(User).options(joinedload(User.seguridades)).filter(User.id_usuario == item_id).first()
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
    return item.to_dict()


@router.delete("/{item_id}", summary='Eliminar usuario', description='Elimina un usuario por `id_usuario`.')
def delete_usuario(item_id: int, db: Session = Depends(get_db)):
    item = db.get(User, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}
