from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.estado_oe import EstadoOe
from app.schemas.estado_oe import EstadoOeCreate, EstadoOeRead, EstadoOeUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/estado_oe", tags=["estado_oe"])


@router.post("/", response_model=EstadoOeRead, summary='POST Estado Oe', description='POST Estado Oe endpoint. Replace this placeholder with a meaningful description.')
def create_estado_oe(payload: EstadoOeCreate, db: Session = Depends(get_db)):
    obj = EstadoOe(nombre=payload.nombre)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Estado Oe', description='GET Estado Oe endpoint. Replace this placeholder with a meaningful description.')
def list_estado_oe(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(EstadoOe).count()
    
    # Obtener elementos de la página actual
    items = db.query(EstadoOe).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=EstadoOeRead, summary='GET Estado Oe', description='GET Estado Oe endpoint. Replace this placeholder with a meaningful description.')
def get_estado_oe(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoOe, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOe not found")
    return item


@router.put("/{item_id}", response_model=EstadoOeRead, summary='PUT Estado Oe', description='PUT Estado Oe endpoint. Replace this placeholder with a meaningful description.')
def update_estado_oe(item_id: int, payload: EstadoOeUpdate, db: Session = Depends(get_db)):
    item = db.get(EstadoOe, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOe not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Estado Oe', description='DELETE Estado Oe endpoint. Replace this placeholder with a meaningful description.')
def delete_estado_oe(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoOe, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOe not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
