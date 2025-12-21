from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.estado_proforma import EstadoProforma
from app.schemas.estado_proforma import (
EstadoProformaCreate,
    EstadoProformaRead,
    EstadoProformaUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/estado_proforma", tags=["estado_proforma"])

@router.post("/", response_model=EstadoProformaRead, summary='POST Estado Proforma', description='POST Estado Proforma endpoint. Replace this placeholder with a meaningful description.')
def create_estado_proforma(payload: EstadoProformaCreate, db: Session = Depends(get_db)):
    obj = EstadoProforma(nombre=payload.nombre)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/", response_model=List[EstadoProformaRead], summary='GET Estado Proforma', description='GET Estado Proforma endpoint. Replace this placeholder with a meaningful description.')
def list_estado_proforma(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(EstadoProforma).offset(skip).limit(limit).all()
    return items

@router.get("/{item_id}", response_model=EstadoProformaRead, summary='GET Estado Proforma', description='GET Estado Proforma endpoint. Replace this placeholder with a meaningful description.')
def get_estado_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoProforma not found")
    return item

@router.put("/{item_id}", response_model=EstadoProformaRead, summary='PUT Estado Proforma', description='PUT Estado Proforma endpoint. Replace this placeholder with a meaningful description.')
def update_estado_proforma(item_id: int, payload: EstadoProformaUpdate, db: Session = Depends(get_db)):
    item = db.get(EstadoProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoProforma not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", summary='DELETE Estado Proforma', description='DELETE Estado Proforma endpoint. Replace this placeholder with a meaningful description.')
def delete_estado_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoProforma not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
