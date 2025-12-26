from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.puerto import Puerto
from app.schemas.puerto import PuertoCreate, PuertoRead, PuertoUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Puerto
PaginatedPuertoResponse = create_paginated_response_model(PuertoRead)

router = APIRouter(prefix="/puerto", tags=["puerto"])


@router.post("/", response_model=PuertoRead, summary='POST Puerto', description='Crear un nuevo puerto.')
def create_puerto(payload: PuertoCreate, db: Session = Depends(get_db)):
    obj = Puerto(
        nombre=payload.nombre, 
        #codigo=payload.codigo,
        descripcion=payload.descripcion
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedPuertoResponse, summary='GET Puerto', description='Obtener lista de puertos con paginación.')
def list_puerto(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Puerto).count()
    
    # Obtener elementos de la página actual
    items = db.query(Puerto).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=PuertoRead, summary='GET Puerto', description='Obtener un puerto específico por ID.')
def get_puerto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Puerto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Puerto not found")
    return item


@router.put("/{item_id}", response_model=PuertoRead, summary='PUT Puerto', description='Actualizar un puerto existente.')
def update_puerto(item_id: int, payload: PuertoUpdate, db: Session = Depends(get_db)):
    item = db.get(Puerto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Puerto not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Puerto', description='Eliminar un puerto.')
def delete_puerto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Puerto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Puerto not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
