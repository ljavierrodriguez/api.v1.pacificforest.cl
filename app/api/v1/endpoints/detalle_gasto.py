from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.detalle_gasto import DetalleGasto
from app.schemas.detalle_gasto import (
DetalleGastoCreate,
    DetalleGastoRead,
    DetalleGastoUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/detalle_gasto", tags=["detalle_gasto"])


@router.post("/", response_model=DetalleGastoRead, summary='POST Detalle Gasto', description='POST Detalle Gasto endpoint. Replace this placeholder with a meaningful description.')
def create_detalle(payload: DetalleGastoCreate, db: Session = Depends(get_db)):
    obj = DetalleGasto(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Detalle Gasto', description='GET Detalle Gasto endpoint. Replace this placeholder with a meaningful description.')
def list_detalles(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(DetalleGasto).count()
    
    # Obtener elementos de la página actual
    items = db.query(DetalleGasto).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=DetalleGastoRead, summary='GET Detalle Gasto', description='GET Detalle Gasto endpoint. Replace this placeholder with a meaningful description.')
def get_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleGasto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=DetalleGastoRead, summary='PUT Detalle Gasto', description='PUT Detalle Gasto endpoint. Replace this placeholder with a meaningful description.')
def update_detalle(item_id: int, payload: DetalleGastoUpdate, db: Session = Depends(get_db)):
    item = db.get(DetalleGasto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Detalle Gasto', description='DELETE Detalle Gasto endpoint. Replace this placeholder with a meaningful description.')
def delete_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleGasto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
