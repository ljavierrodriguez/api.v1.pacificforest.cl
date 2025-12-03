from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.estado_odc import EstadoOdc
from app.schemas.estado_odc import EstadoOdcCreate, EstadoOdcRead, EstadoOdcUpdate

router = APIRouter(prefix="/estado_odc", tags=["estado_odc"])


@router.post("/", response_model=EstadoOdcRead, summary='POST Estado Odc', description='POST Estado Odc endpoint. Replace this placeholder with a meaningful description.')
def create_estado_odc(payload: EstadoOdcCreate, db: Session = Depends(get_db)):
    obj = EstadoOdc(nombre=payload.nombre)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[EstadoOdcRead], summary='GET Estado Odc', description='GET Estado Odc endpoint. Replace this placeholder with a meaningful description.')
def list_estado_odc(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(EstadoOdc).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=EstadoOdcRead, summary='GET Estado Odc', description='GET Estado Odc endpoint. Replace this placeholder with a meaningful description.')
def get_estado_odc(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoOdc, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOdc not found")
    return item


@router.put("/{item_id}", response_model=EstadoOdcRead, summary='PUT Estado Odc', description='PUT Estado Odc endpoint. Replace this placeholder with a meaningful description.')
def update_estado_odc(item_id: int, payload: EstadoOdcUpdate, db: Session = Depends(get_db)):
    item = db.get(EstadoOdc, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOdc not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Estado Odc', description='DELETE Estado Odc endpoint. Replace this placeholder with a meaningful description.')
def delete_estado_odc(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoOdc, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOdc not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
