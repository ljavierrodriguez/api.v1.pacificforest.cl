from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.estado_orden_servicio import EstadoOrdenServicio
from app.schemas.estado_orden_servicio import (
    EstadoOrdenServicioCreate,
    EstadoOrdenServicioRead,
    EstadoOrdenServicioUpdate,
)

router = APIRouter(prefix="/estado_orden_servicio", tags=["estado_orden_servicio"])


@router.post("/", response_model=EstadoOrdenServicioRead, status_code=201)
def create_estado_orden_servicio(payload: EstadoOrdenServicioCreate, db: Session = Depends(get_db)):
    obj = EstadoOrdenServicio(nombre=payload.nombre)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[EstadoOrdenServicioRead])
def list_estado_orden_servicio(db: Session = Depends(get_db)):
    return db.query(EstadoOrdenServicio).all()


@router.get("/{item_id}", response_model=EstadoOrdenServicioRead)
def get_estado_orden_servicio(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoOrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOrdenServicio not found")
    return item


@router.put("/{item_id}", response_model=EstadoOrdenServicioRead)
def update_estado_orden_servicio(item_id: int, payload: EstadoOrdenServicioUpdate, db: Session = Depends(get_db)):
    item = db.get(EstadoOrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOrdenServicio not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_estado_orden_servicio(item_id: int, db: Session = Depends(get_db)):
    item = db.get(EstadoOrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="EstadoOrdenServicio not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
