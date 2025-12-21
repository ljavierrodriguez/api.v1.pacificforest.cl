from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoRead, ProductoUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/producto", tags=["producto"])


@router.post("/", response_model=ProductoRead, summary='POST Producto', description='POST Producto endpoint. Replace this placeholder with a meaningful description.')
def create_producto(payload: ProductoCreate, db: Session = Depends(get_db)):
    obj = Producto(
        id_clase=payload.id_clase,
        id_especie=payload.id_especie,
        nombre_producto_esp=payload.nombre_producto_esp,
        nombre_producto_ing=payload.nombre_producto_ing,
        obs_calidad=payload.obs_calidad,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Producto', description='GET Producto endpoint. Replace this placeholder with a meaningful description.')
def list_producto(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Producto).count()
    
    # Obtener elementos de la página actual
    items = db.query(Producto).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ProductoRead, summary='GET Producto', description='GET Producto endpoint. Replace this placeholder with a meaningful description.')
def get_producto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Producto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Producto not found")
    return item


@router.put("/{item_id}", response_model=ProductoRead, summary='PUT Producto', description='PUT Producto endpoint. Replace this placeholder with a meaningful description.')
def update_producto(item_id: int, payload: ProductoUpdate, db: Session = Depends(get_db)):
    item = db.get(Producto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Producto not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Producto', description='DELETE Producto endpoint. Replace this placeholder with a meaningful description.')
def delete_producto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Producto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Producto not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
