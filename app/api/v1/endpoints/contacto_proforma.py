from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.contacto_proforma import ContactoProforma
from app.schemas.contacto_proforma import (
ContactoProformaCreate,
    ContactoProformaRead,
    ContactoProformaUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/contacto_proforma", tags=["contacto_proforma"])


@router.post("/", response_model=ContactoProformaRead, summary='POST Contacto Proforma', description='POST Contacto Proforma endpoint. Replace this placeholder with a meaningful description.')
def create_contacto_proforma(payload: ContactoProformaCreate, db: Session = Depends(get_db)):
    obj = ContactoProforma(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[ContactoProformaRead], summary='GET Contacto Proforma', description='GET Contacto Proforma endpoint. Replace this placeholder with a meaningful description.')
def list_contactos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ContactoProforma).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=ContactoProformaRead, summary='GET Contacto Proforma', description='GET Contacto Proforma endpoint. Replace this placeholder with a meaningful description.')
def get_contacto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ContactoProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=ContactoProformaRead, summary='PUT Contacto Proforma', description='PUT Contacto Proforma endpoint. Replace this placeholder with a meaningful description.')
def update_contacto(item_id: int, payload: ContactoProformaUpdate, db: Session = Depends(get_db)):
    item = db.get(ContactoProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Contacto Proforma', description='DELETE Contacto Proforma endpoint. Replace this placeholder with a meaningful description.')
def delete_contacto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ContactoProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
