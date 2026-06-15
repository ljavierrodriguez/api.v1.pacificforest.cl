from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.contacto_orden_servicio import ContactoOrdenServicio
from app.schemas.contacto_orden_servicio import (
    ContactoOrdenServicioCreate,
    ContactoOrdenServicioRead,
    ContactoOrdenServicioUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/contacto_orden_servicio", tags=["contacto_orden_servicio"])


def _serialize(item: ContactoOrdenServicio) -> dict:
    contacto = getattr(item, "Contacto", None)
    return {
        "id_contacto_orden_servicio": item.id_contacto_orden_servicio,
        "id_contacto": item.id_contacto,
        "id_orden_servicio": item.id_orden_servicio,
        "contacto_nombre": getattr(contacto, "nombre", None),
        "contacto_correo": getattr(contacto, "correo", None),
        "contacto_telefono": getattr(contacto, "telefono", None),
    }


@router.post("/", response_model=ContactoOrdenServicioRead, summary="POST Contacto Orden Servicio")
def create_contacto_orden_servicio(payload: ContactoOrdenServicioCreate, db: Session = Depends(get_db)):
    obj = ContactoOrdenServicio(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _serialize(obj)


@router.get("/", summary="GET Contacto Orden Servicio - Listado paginado")
def list_contacto_orden_servicio(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    id_orden_servicio: Optional[int] = Query(None, description="Filtrar por id_orden_servicio"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    query = db.query(ContactoOrdenServicio)
    if id_orden_servicio is not None:
        query = query.filter(ContactoOrdenServicio.id_orden_servicio == id_orden_servicio)
    total_items = query.count()
    items = query.offset(skip).limit(page_size).all()
    return create_paginated_response([_serialize(i) for i in items], page, page_size, total_items)


@router.get(
    "/by-orden/{id_orden_servicio}",
    response_model=List[ContactoOrdenServicioRead],
    summary="GET Contactos por Orden de Servicio",
    description="Obtiene todos los contactos asociados a una orden de servicio. Responde arreglo vacío si no hay.",
)
def list_by_orden_servicio(id_orden_servicio: int, db: Session = Depends(get_db)):
    items = db.query(ContactoOrdenServicio).filter(
        ContactoOrdenServicio.id_orden_servicio == id_orden_servicio
    ).all()
    return [_serialize(i) for i in items]


@router.get("/{item_id}", response_model=ContactoOrdenServicioRead, summary="GET Contacto Orden Servicio por ID")
def get_contacto_orden_servicio(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ContactoOrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ContactoOrdenServicio not found")
    return _serialize(item)


@router.put("/{item_id}", response_model=ContactoOrdenServicioRead, summary="PUT Contacto Orden Servicio")
def update_contacto_orden_servicio(item_id: int, payload: ContactoOrdenServicioUpdate, db: Session = Depends(get_db)):
    item = db.get(ContactoOrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ContactoOrdenServicio not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


@router.delete("/{item_id}", summary="DELETE Contacto Orden Servicio")
def delete_contacto_orden_servicio(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ContactoOrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ContactoOrdenServicio not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
