from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.detalle_pl import DetallePl
from app.schemas.detalle_pl import (
    DetallePlCreate,
    DetallePlRead,
    DetallePlUpdate,
)

router = APIRouter(prefix="/detalle_pl", tags=["detalle_pl"])


@router.post("/", response_model=DetallePlRead, summary='POST Detalle Pl', description='POST Detalle Pl endpoint. Replace this placeholder with a meaningful description.')
def create_detalle(payload: DetallePlCreate, db: Session = Depends(get_db)):
    obj = DetallePl(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[DetallePlRead], summary='GET Detalle Pl', description='GET Detalle Pl endpoint. Replace this placeholder with a meaningful description.')
def list_detalles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DetallePl).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=DetallePlRead, summary='GET Detalle Pl', description='GET Detalle Pl endpoint. Replace this placeholder with a meaningful description.')
def get_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetallePl, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=DetallePlRead, summary='PUT Detalle Pl', description='PUT Detalle Pl endpoint. Replace this placeholder with a meaningful description.')
def update_detalle(item_id: int, payload: DetallePlUpdate, db: Session = Depends(get_db)):
    item = db.get(DetallePl, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Detalle Pl', description='DELETE Detalle Pl endpoint. Replace this placeholder with a meaningful description.')
def delete_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetallePl, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
