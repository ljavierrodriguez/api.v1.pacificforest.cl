from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.ciudad import Ciudad
from app.schemas.ciudad import CiudadCreate, CiudadRead, CiudadUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Ciudad
PaginatedCiudadResponse = create_paginated_response_model(CiudadRead)

router = APIRouter(prefix="/ciudad", tags=["ciudad"])


@router.post("/", response_model=CiudadRead, status_code=201, summary='POST Ciudad', description='Crear una nueva ciudad.')
def create_ciudad(payload: CiudadCreate, db: Session = Depends(get_db)):
    obj = Ciudad(nombre=payload.nombre, id_pais=payload.id_pais)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedCiudadResponse, summary='GET Ciudad', description='Obtener lista de ciudades con paginación.')
def list_ciudad(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Ciudad).count()
    
    # Obtener elementos de la página actual
    items = db.query(Ciudad).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=CiudadRead, summary='GET Ciudad', description='Obtener una ciudad específica por ID.')
def get_ciudad(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ciudad, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ciudad not found")
    return item


@router.put("/{item_id}", response_model=CiudadRead, summary='PUT Ciudad', description='Actualizar una ciudad existente.')
def update_ciudad(item_id: int, payload: CiudadUpdate, db: Session = Depends(get_db)):
    item = db.get(Ciudad, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ciudad not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Ciudad', description='Eliminar una ciudad.')
def delete_ciudad(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ciudad, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ciudad not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
