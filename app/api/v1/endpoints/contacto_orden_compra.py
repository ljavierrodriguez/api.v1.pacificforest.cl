from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.contacto_orden_compra import ContactoOrdenCompra
from app.schemas.contacto_orden_compra import (
ContactoOrdenCompraCreate,
    ContactoOrdenCompraRead,
    ContactoOrdenCompraUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/contacto_orden_compra", tags=["contacto_orden_compra"])


@router.post("/", response_model=ContactoOrdenCompraRead, summary='POST Contacto Orden Compra', description='POST Contacto Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def create_contacto(payload: ContactoOrdenCompraCreate, db: Session = Depends(get_db)):
    obj = ContactoOrdenCompra(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Contacto Orden Compra', description='GET Contacto Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def list_contactos(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(ContactoOrdenCompra).count()
    
    # Obtener elementos de la página actual
    items = db.query(ContactoOrdenCompra).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ContactoOrdenCompraRead, summary='GET Contacto Orden Compra', description='GET Contacto Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def get_contacto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ContactoOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=ContactoOrdenCompraRead, summary='PUT Contacto Orden Compra', description='PUT Contacto Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def update_contacto(item_id: int, payload: ContactoOrdenCompraUpdate, db: Session = Depends(get_db)):
    item = db.get(ContactoOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Contacto Orden Compra', description='DELETE Contacto Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def delete_contacto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ContactoOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
