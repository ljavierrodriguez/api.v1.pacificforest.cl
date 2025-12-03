from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.direccion import Direccion
from app.schemas.direccion import DireccionCreate, DireccionRead, DireccionUpdate
from app.db.session import get_db

router = APIRouter(prefix="/direcciones", tags=["direcciones"])


@router.post("/", response_model=DireccionRead, status_code=201, summary='POST Direccion', description='POST Direccion endpoint. Replace this placeholder with a meaningful description.')
def create_direccion(payload: DireccionCreate, db: Session = Depends(get_db)):
    obj = Direccion(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[DireccionRead], summary='GET Direccion', description='GET Direccion endpoint. Replace this placeholder with a meaningful description.')
def list_direcciones(db: Session = Depends(get_db)):
    return db.query(Direccion).all()


@router.get("/{item_id}", response_model=DireccionRead, summary='GET Direccion', description='GET Direccion endpoint. Replace this placeholder with a meaningful description.')
def get_direccion(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Direccion, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Direccion no encontrada")
    return obj


@router.put("/{item_id}", response_model=DireccionRead, summary='PUT Direccion', description='PUT Direccion endpoint. Replace this placeholder with a meaningful description.')
def update_direccion(item_id: int, payload: DireccionUpdate, db: Session = Depends(get_db)):
    obj = db.get(Direccion, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Direccion no encontrada")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=204, summary='DELETE Direccion', description='DELETE Direccion endpoint. Replace this placeholder with a meaningful description.')
def delete_direccion(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Direccion, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Direccion no encontrada")
    db.delete(obj)
    db.commit()
    return
