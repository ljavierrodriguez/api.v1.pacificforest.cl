from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.clase import Clase
from app.schemas.clase import ClaseCreate, ClaseRead, ClaseUpdate

router = APIRouter(prefix="/clase", tags=["clase"])


@router.post("/", response_model=ClaseRead, summary='POST Clase', description='POST Clase endpoint. Replace this placeholder with a meaningful description.')
def create_clase(payload: ClaseCreate, db: Session = Depends(get_db)):
    obj = Clase(nombre=payload.nombre)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[ClaseRead], summary='GET Clase', description='GET Clase endpoint. Replace this placeholder with a meaningful description.')
def list_clase(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Clase).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=ClaseRead, summary='GET Clase', description='GET Clase endpoint. Replace this placeholder with a meaningful description.')
def get_clase(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Clase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clase not found")
    return item


@router.put("/{item_id}", response_model=ClaseRead, summary='PUT Clase', description='PUT Clase endpoint. Replace this placeholder with a meaningful description.')
def update_clase(item_id: int, payload: ClaseUpdate, db: Session = Depends(get_db)):
    item = db.get(Clase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clase not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Clase', description='DELETE Clase endpoint. Replace this placeholder with a meaningful description.')
def delete_clase(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Clase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clase not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
