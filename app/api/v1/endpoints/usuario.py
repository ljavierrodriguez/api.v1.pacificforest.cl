from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import List
from sqlalchemy.orm import Session, joinedload
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.models.usuario import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Usuario
PaginatedUserResponse = create_paginated_response_model(UserRead)

router = APIRouter(prefix="/usuario", tags=["usuario"])


@router.post("/", response_model=UserRead, summary='Crear usuario', description='Crear un nuevo usuario.')
def create_usuario(payload: UserCreate, db: Session = Depends(get_db)):
    # Normalizar login a minúsculas para hacerlo case-insensitive
    login_lower = payload.login.lower() if payload.login else ""
    
    # Validar unicidad de login y correo
    if db.query(User).filter(User.login == login_lower).first():
        raise HTTPException(status_code=400, detail="El login ya existe")
    if db.query(User).filter(User.correo == str(payload.correo)).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user = User(
        login=login_lower,
        nombre=payload.nombre,
        correo=str(payload.correo),
        url_firma=payload.url_firma,
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
        # Normalizar login a minúsculas
        login_lower = data["login"].lower() if data["login"] else ""
        if db.query(User).filter(User.login == login_lower).first():
            raise HTTPException(status_code=400, detail="El login ya existe")
        item.login = login_lower

    if "correo" in data and str(data["correo"]) != item.correo:
        if db.query(User).filter(User.correo == str(data["correo"]) ).first():
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        item.correo = str(data["correo"])

    if "password" in data and data["password"]:
        item.set_password(data["password"])

    # Campos directos
    for field in ("nombre", "telefono", "activo", "url_firma"):
        if field in data:
            setattr(item, field, data[field])

    db.add(item)
    db.commit()
    db.refresh(item)
    return item.to_dict()


@router.post("/{item_id}/firma", summary='Subir firma del usuario', description='Sube una imagen de firma para el usuario.')
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


@router.delete("/{item_id}", summary='Eliminar usuario', description='Elimina un usuario por `id_usuario`.')
def delete_usuario(item_id: int, db: Session = Depends(get_db)):
    item = db.get(User, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(item)
    db.commit()
    return {"ok": True}
