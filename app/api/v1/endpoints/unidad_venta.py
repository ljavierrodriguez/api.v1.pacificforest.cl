from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.unidad_venta import UnidadVenta
from app.schemas.unidad_venta import UnidadVentaCreate, UnidadVentaRead, UnidadVentaUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/unidad_venta", tags=["unidad_venta"])


@router.post("/", response_model=UnidadVentaRead, summary='POST Unidad Venta', description='POST Unidad Venta endpoint. Replace this placeholder with a meaningful description.')
def create_unidad_venta(payload: UnidadVentaCreate, db: Session = Depends(get_db)):
    obj = UnidadVenta(
        nombre=payload.nombre,
        cubicacion=payload.cubicacion,
        descripcion=payload.descripcion,
        por_defecto=payload.por_defecto,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Unidad Venta', description='GET Unidad Venta endpoint. Replace this placeholder with a meaningful description.')
def list_unidad_venta(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(UnidadVenta).count()
    
    # Obtener elementos de la página actual
    items = db.query(UnidadVenta).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=UnidadVentaRead, summary='GET Unidad Venta', description='GET Unidad Venta endpoint. Replace this placeholder with a meaningful description.')
def get_unidad_venta(item_id: int, db: Session = Depends(get_db)):
    item = db.get(UnidadVenta, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="UnidadVenta not found")
    return item


@router.put("/{item_id}", response_model=UnidadVentaRead, summary='PUT Unidad Venta', description='PUT Unidad Venta endpoint. Replace this placeholder with a meaningful description.')
def update_unidad_venta(item_id: int, payload: UnidadVentaUpdate, db: Session = Depends(get_db)):
    item = db.get(UnidadVenta, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="UnidadVenta not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Unidad Venta', description='DELETE Unidad Venta endpoint. Replace this placeholder with a meaningful description.')
def delete_unidad_venta(item_id: int, db: Session = Depends(get_db)):
    item = db.get(UnidadVenta, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="UnidadVenta not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
