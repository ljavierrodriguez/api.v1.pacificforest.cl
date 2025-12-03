from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.especie import EspecieCreate, EspecieRead, EspecieUpdate
from app.models.especie import Especie
from app.db.session import get_db

router = APIRouter(prefix="/especies", tags=["especies"])


@router.post("/", response_model=EspecieRead, status_code=201, summary='POST Especie', description='POST Especie endpoint. Replace this placeholder with a meaningful description.')
def create_especie(payload: EspecieCreate, db: Session = Depends(get_db)):
    obj = Especie(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[EspecieRead], summary='GET Especie', description='GET Especie endpoint. Replace this placeholder with a meaningful description.')
def list_especies(db: Session = Depends(get_db)):
    return db.query(Especie).all()


@router.get("/{item_id}", response_model=EspecieRead, summary='GET Especie', description='GET Especie endpoint. Replace this placeholder with a meaningful description.')
def get_especie(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Especie, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    return obj


@router.put("/{item_id}", response_model=EspecieRead, summary='PUT Especie', description='PUT Especie endpoint. Replace this placeholder with a meaningful description.')
def update_especie(item_id: int, payload: EspecieUpdate, db: Session = Depends(get_db)):
    obj = db.get(Especie, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=204, summary='DELETE Especie', description='DELETE Especie endpoint. Replace this placeholder with a meaningful description.')
def delete_especie(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Especie, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Especie no encontrada")
    db.delete(obj)
    db.commit()
    return
