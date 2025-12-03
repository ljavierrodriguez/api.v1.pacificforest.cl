from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.contacto import Contacto
from app.schemas.contacto import ContactoCreate, ContactoRead, ContactoUpdate

router = APIRouter(prefix="/contacto", tags=["contacto"])


@router.post("/", response_model=ContactoRead, summary='POST Contacto', description='POST Contacto endpoint. Replace this placeholder with a meaningful description.')
def create_contacto(payload: ContactoCreate, db: Session = Depends(get_db)):
    obj = Contacto(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[ContactoRead], summary='GET Contacto', description='GET Contacto endpoint. Replace this placeholder with a meaningful description.')
def list_contactos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Contacto).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=ContactoRead, summary='GET Contacto', description='GET Contacto endpoint. Replace this placeholder with a meaningful description.')
def get_contacto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Contacto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=ContactoRead, summary='PUT Contacto', description='PUT Contacto endpoint. Replace this placeholder with a meaningful description.')
def update_contacto(item_id: int, payload: ContactoUpdate, db: Session = Depends(get_db)):
    item = db.get(Contacto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Contacto', description='DELETE Contacto endpoint. Replace this placeholder with a meaningful description.')
def delete_contacto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Contacto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
