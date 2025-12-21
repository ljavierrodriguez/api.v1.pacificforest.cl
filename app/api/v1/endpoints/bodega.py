from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.bodega import Bodega
from app.schemas.bodega import BodegaCreate, BodegaRead, BodegaUpdate

router = APIRouter(prefix="/bodega", tags=["bodega"])


@router.post("/", response_model=BodegaRead, status_code=201, summary='POST Bodega', description='Crear una nueva bodega.')
def create_bodega(payload: BodegaCreate, db: Session = Depends(get_db)):
    obj = Bodega(
        nombre=payload.nombre,
        direccion=payload.direccion,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[BodegaRead], summary='GET Bodega', description='Obtener lista de bodegas con paginación.')
def list_bodega(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Bodega).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=BodegaRead, summary='GET Bodega', description='Obtener una bodega específica por ID.')
def get_bodega(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Bodega, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Bodega not found")
    return item


@router.put("/{item_id}", response_model=BodegaRead, summary='PUT Bodega', description='Actualizar una bodega existente.')
def update_bodega(item_id: int, payload: BodegaUpdate, db: Session = Depends(get_db)):
    item = db.get(Bodega, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Bodega not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Bodega', description='Eliminar una bodega.')
def delete_bodega(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Bodega, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Bodega not found")
    db.delete(item)
    db.commit()
    return {"ok": True}