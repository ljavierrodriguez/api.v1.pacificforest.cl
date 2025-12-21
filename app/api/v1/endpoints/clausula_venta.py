from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.clausula_venta import ClausulaVenta
from app.schemas.clausula_venta import ClausulaVentaCreate, ClausulaVentaRead, ClausulaVentaUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/clausula_venta", tags=["clausula_venta"])


@router.post("/", response_model=ClausulaVentaRead, summary='POST Clausula Venta', description='POST Clausula Venta endpoint. Replace this placeholder with a meaningful description.')
def create_clausula(payload: ClausulaVentaCreate, db: Session = Depends(get_db)):
    obj = ClausulaVenta(texto=payload.texto)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Clausula Venta', description='Obtener lista de cláusulas de venta con paginación.')
def list_clausula(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(ClausulaVenta).count()
    
    # Obtener elementos de la página actual
    items = db.query(ClausulaVenta).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ClausulaVentaRead, summary='GET Clausula Venta', description='GET Clausula Venta endpoint. Replace this placeholder with a meaningful description.')
def get_clausula(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClausulaVenta, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClausulaVenta not found")
    return item


@router.put("/{item_id}", response_model=ClausulaVentaRead, summary='PUT Clausula Venta', description='PUT Clausula Venta endpoint. Replace this placeholder with a meaningful description.')
def update_clausula(item_id: int, payload: ClausulaVentaUpdate, db: Session = Depends(get_db)):
    item = db.get(ClausulaVenta, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClausulaVenta not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Clausula Venta', description='DELETE Clausula Venta endpoint. Replace this placeholder with a meaningful description.')
def delete_clausula(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClausulaVenta, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClausulaVenta not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
