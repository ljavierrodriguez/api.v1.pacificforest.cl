from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.detalle_ide import DetalleIde
from app.schemas.detalle_ide import (
DetalleIdeCreate,
    DetalleIdeRead,
    DetalleIdeUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/detalle_ide", tags=["detalle_ide"])


@router.post("/", response_model=DetalleIdeRead, summary='POST Detalle Ide', description='POST Detalle Ide endpoint. Replace this placeholder with a meaningful description.')
def create_detalle(payload: DetalleIdeCreate, db: Session = Depends(get_db)):
    obj = DetalleIde(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[DetalleIdeRead], summary='GET Detalle Ide', description='GET Detalle Ide endpoint. Replace this placeholder with a meaningful description.')
def list_detalles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DetalleIde).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=DetalleIdeRead, summary='GET Detalle Ide', description='GET Detalle Ide endpoint. Replace this placeholder with a meaningful description.')
def get_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleIde, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=DetalleIdeRead, summary='PUT Detalle Ide', description='PUT Detalle Ide endpoint. Replace this placeholder with a meaningful description.')
def update_detalle(item_id: int, payload: DetalleIdeUpdate, db: Session = Depends(get_db)):
    item = db.get(DetalleIde, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Detalle Ide', description='DELETE Detalle Ide endpoint. Replace this placeholder with a meaningful description.')
def delete_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleIde, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
