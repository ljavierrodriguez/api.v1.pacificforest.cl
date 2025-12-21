from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.schemas.detalle_orden_compra import (
DetalleOrdenCompraCreate,
    DetalleOrdenCompraRead,
    DetalleOrdenCompraUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/detalle_orden_compra", tags=["detalle_orden_compra"])


@router.post("/", response_model=DetalleOrdenCompraRead, summary='POST Detalle Orden Compra', description='POST Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def create_detalle(payload: DetalleOrdenCompraCreate, db: Session = Depends(get_db)):
    obj = DetalleOrdenCompra(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Detalle Orden Compra', description='GET Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def list_detalles(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(DetalleOrdenCompra).count()
    
    # Obtener elementos de la página actual
    items = db.query(DetalleOrdenCompra).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=DetalleOrdenCompraRead, summary='GET Detalle Orden Compra', description='GET Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def get_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=DetalleOrdenCompraRead, summary='PUT Detalle Orden Compra', description='PUT Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def update_detalle(item_id: int, payload: DetalleOrdenCompraUpdate, db: Session = Depends(get_db)):
    item = db.get(DetalleOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Detalle Orden Compra', description='DELETE Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def delete_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
