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


@router.get("/", response_model=List[DetalleOrdenCompraRead], summary='GET Detalle Orden Compra', description='GET Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def list_detalles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DetalleOrdenCompra).offset(skip).limit(limit).all()


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
