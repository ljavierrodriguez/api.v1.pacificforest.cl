from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.moneda import Moneda
from app.schemas.moneda import MonedaCreate, MonedaRead, MonedaUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/moneda", tags=["moneda"])


@router.post("/", response_model=MonedaRead, summary='POST Moneda', description='POST Moneda endpoint. Replace this placeholder with a meaningful description.')
def create_moneda(payload: MonedaCreate, db: Session = Depends(get_db)):
    obj = Moneda(
        id_moneda=payload.id_moneda,
        etiqueta=payload.etiqueta,
        nombre_moneda=payload.nombre_moneda,
        por_defecto=payload.por_defecto,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Moneda', description='GET Moneda endpoint. Replace this placeholder with a meaningful description.')
def list_moneda(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Moneda).count()
    
    # Obtener elementos de la página actual
    items = db.query(Moneda).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=MonedaRead, summary='GET Moneda', description='GET Moneda endpoint. Replace this placeholder with a meaningful description.')
def get_moneda(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Moneda, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Moneda not found")
    return item


@router.put("/{item_id}", response_model=MonedaRead, summary='PUT Moneda', description='PUT Moneda endpoint. Replace this placeholder with a meaningful description.')
def update_moneda(item_id: int, payload: MonedaUpdate, db: Session = Depends(get_db)):
    item = db.get(Moneda, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Moneda not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Moneda', description='DELETE Moneda endpoint. Replace this placeholder with a meaningful description.')
def delete_moneda(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Moneda, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Moneda not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
