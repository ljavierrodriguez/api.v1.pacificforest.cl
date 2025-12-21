from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.schemas.seguridad import SeguridadCreate, SeguridadRead, SeguridadUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model
from app.models.seguridad import Seguridad
from app.models.usuario import User
from app.db.session import get_db

# Crear el modelo de respuesta paginada para Seguridad
PaginatedSeguridadResponse = create_paginated_response_model(SeguridadRead)

router = APIRouter(prefix="/seguridad", tags=["seguridad"])


@router.post("/", response_model=SeguridadRead, status_code=201, summary='Crear seguridad', description='Crea un nuevo registro de seguridad para un usuario y módulo.')
def create_seguridad(payload: SeguridadCreate, db: Session = Depends(get_db)):
    # Verificar que el usuario existe
    usuario = db.query(User).filter(User.id_usuario == payload.id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que no existe ya un registro para este usuario y módulo
    existe = db.query(Seguridad).filter(
        Seguridad.id_usuario == payload.id_usuario,
        Seguridad.modulo == payload.modulo
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un registro de seguridad para el usuario {payload.id_usuario} y el módulo '{payload.modulo}'"
        )
    
    seguridad = Seguridad(
        id_usuario=payload.id_usuario,
        modulo=payload.modulo,
        crear=payload.crear,
        ver=payload.ver,
        editar=payload.editar,
        eliminar=payload.eliminar
    )
    db.add(seguridad)
    db.commit()
    db.refresh(seguridad)
    return seguridad


@router.get("/", response_model=PaginatedSeguridadResponse, summary='Listar seguridades', description='Lista todos los registros de seguridad con paginación.')
def list_seguridades(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Seguridad).count()
    
    # Obtener elementos de la página actual
    items = db.query(Seguridad).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{id_seguridad}", response_model=SeguridadRead, summary='Obtener seguridad', description='Obtiene un registro de seguridad por su ID.')
def get_seguridad(id_seguridad: int, db: Session = Depends(get_db)):
    item = db.query(Seguridad).filter(Seguridad.id_seguridad == id_seguridad).first()
    if not item:
        raise HTTPException(status_code=404, detail="Seguridad no encontrada")
    return item


@router.get("/usuario/{id_usuario}", response_model=List[SeguridadRead], summary='Obtener seguridades por usuario', description='Obtiene todos los registros de seguridad de un usuario específico.')
def get_seguridades_by_usuario(id_usuario: int, db: Session = Depends(get_db)):
    # Verificar que el usuario existe
    usuario = db.query(User).filter(User.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    items = db.query(Seguridad).filter(Seguridad.id_usuario == id_usuario).all()
    return items


@router.put("/{id_seguridad}", response_model=SeguridadRead, summary='Actualizar seguridad', description='Actualiza un registro de seguridad existente.')
def update_seguridad(id_seguridad: int, payload: SeguridadUpdate, db: Session = Depends(get_db)):
    item = db.query(Seguridad).filter(Seguridad.id_seguridad == id_seguridad).first()
    if not item:
        raise HTTPException(status_code=404, detail="Seguridad no encontrada")
    
    # Si se cambia el usuario, verificar que existe
    if payload.id_usuario is not None and payload.id_usuario != item.id_usuario:
        usuario = db.query(User).filter(User.id_usuario == payload.id_usuario).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Si se cambia el módulo o usuario, verificar que no existe ya otro registro con esa combinación
    nuevo_modulo = payload.modulo if payload.modulo is not None else item.modulo
    nuevo_usuario = payload.id_usuario if payload.id_usuario is not None else item.id_usuario
    
    if nuevo_modulo != item.modulo or nuevo_usuario != item.id_usuario:
        existe = db.query(Seguridad).filter(
            Seguridad.id_usuario == nuevo_usuario,
            Seguridad.modulo == nuevo_modulo,
            Seguridad.id_seguridad != id_seguridad
        ).first()
        
        if existe:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un registro de seguridad para el usuario {nuevo_usuario} y el módulo '{nuevo_modulo}'"
            )
    
    # Actualizar campos
    if payload.id_usuario is not None:
        item.id_usuario = payload.id_usuario
    if payload.modulo is not None:
        item.modulo = payload.modulo
    if payload.crear is not None:
        item.crear = payload.crear
    if payload.ver is not None:
        item.ver = payload.ver
    if payload.editar is not None:
        item.editar = payload.editar
    if payload.eliminar is not None:
        item.eliminar = payload.eliminar
    
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id_seguridad}", status_code=status.HTTP_204_NO_CONTENT, summary='Eliminar seguridad', description='Elimina un registro de seguridad por su ID.')
def delete_seguridad(id_seguridad: int, db: Session = Depends(get_db)):
    item = db.query(Seguridad).filter(Seguridad.id_seguridad == id_seguridad).first()
    if not item:
        raise HTTPException(status_code=404, detail="Seguridad no encontrada")
    
    db.delete(item)
    db.commit()
    return None

