from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.estado_pl import EstadoPl
from app.schemas.estado_pl import EstadoPlCreate, EstadoPlRead, EstadoPlUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/estado_pl", tags=["estado_pl"])


@router.post("/", response_model=EstadoPlRead, summary='POST Estado Pl', description='POST Estado Pl endpoint. Replace this placeholder with a meaningful description.')
def create_estado_pl(payload: EstadoPlCreate, db: Session = Depends(get_db)):
    obj = EstadoPl(nombre=payload.nombre, es_ple=payload.es_ple, es_plc=payload.es_plc)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[EstadoPlRead], summary='GET Estado Pl', description='GET Estado Pl endpoint. Replace this placeholder with a meaningful description.')
def list_estado_pl(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(EstadoPl).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=EstadoPlRead, summary='GET Estado Pl', description='GET Estado Pl endpoint. Replace this placeholder with a meaningful description.')
def get_estado_pl(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoPl, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoPl not found")
    return item


@router.put("/{item_id}", response_model=EstadoPlRead, summary='PUT Estado Pl', description='PUT Estado Pl endpoint. Replace this placeholder with a meaningful description.')
def update_estado_pl(item_id: int, payload: EstadoPlUpdate, db: Session = Depends(get_db)):
    item = db.get(EstadoPl, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoPl not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Estado Pl', description='DELETE Estado Pl endpoint. Replace this placeholder with a meaningful description.')
def delete_estado_pl(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoPl, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoPl not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
