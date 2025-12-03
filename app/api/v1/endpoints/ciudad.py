from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.ciudad import Ciudad
from app.schemas.ciudad import CiudadCreate, CiudadRead, CiudadUpdate

router = APIRouter(prefix="/ciudad", tags=["ciudad"])


@router.post("/", response_model=CiudadRead, summary='POST Ciudad', description='POST Ciudad endpoint. Replace this placeholder with a meaningful description.')
def create_ciudad(payload: CiudadCreate, db: Session = Depends(get_db)):
    obj = Ciudad(nombre=payload.nombre, id_pais=payload.id_pais)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[CiudadRead], summary='GET Ciudad', description='GET Ciudad endpoint. Replace this placeholder with a meaningful description.')
def list_ciudad(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Ciudad).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=CiudadRead, summary='GET Ciudad', description='GET Ciudad endpoint. Replace this placeholder with a meaningful description.')
def get_ciudad(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ciudad, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ciudad not found")
    return item


@router.put("/{item_id}", response_model=CiudadRead, summary='PUT Ciudad', description='PUT Ciudad endpoint. Replace this placeholder with a meaningful description.')
def update_ciudad(item_id: int, payload: CiudadUpdate, db: Session = Depends(get_db)):
    item = db.get(Ciudad, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ciudad not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Ciudad', description='DELETE Ciudad endpoint. Replace this placeholder with a meaningful description.')
def delete_ciudad(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ciudad, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ciudad not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
