from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.clase import Clase
from app.schemas.clase import ClaseCreate, ClaseRead, ClaseUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Clase
PaginatedClaseResponse = create_paginated_response_model(ClaseRead)

router = APIRouter(prefix="/clase", tags=["clase"])


@router.post("/", response_model=ClaseRead, status_code=201, summary='POST Clase', description='Crear una nueva clase.')
def create_clase(payload: ClaseCreate, db: Session = Depends(get_db)):
    obj = Clase(nombre=payload.nombre, descripcion=payload.descripcion)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedClaseResponse, summary='GET Clase', description='Obtener lista de clases con paginación.')
def list_clase(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Clase).count()
    
    # Obtener elementos de la página actual
    items = db.query(Clase).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ClaseRead, summary='GET Clase', description='Obtener una clase específica por ID.')
def get_clase(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Clase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clase not found")
    return item


@router.put("/{item_id}", response_model=ClaseRead, summary='PUT Clase', description='Actualizar una clase existente.')
def update_clase(item_id: int, payload: ClaseUpdate, db: Session = Depends(get_db)):
    item = db.get(Clase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clase not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Clase', description='Eliminar una clase.')
def delete_clase(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Clase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clase not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
