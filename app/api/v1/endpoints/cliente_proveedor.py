from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.cliente_proveedor import ClienteProveedor
from app.schemas.cliente_proveedor import (
    ClienteProveedorCreate,
    ClienteProveedorRead,
    ClienteProveedorUpdate,
)
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para ClienteProveedor
PaginatedClienteProveedorResponse = create_paginated_response_model(ClienteProveedorRead)

router = APIRouter(prefix="/cliente_proveedor", tags=["cliente_proveedor"])


@router.post("/", response_model=ClienteProveedorRead, summary='POST Cliente Proveedor', description='POST Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def create_cliente_proveedor(
    payload: ClienteProveedorCreate, db: Session = Depends(get_db)
):
    obj = ClienteProveedor(
        rut=payload.rut,
        nombre_fantasia=payload.nombre_fantasia,
        razon_social=payload.razon_social,
        es_nacional=payload.es_nacional,
        giro=payload.giro,
        es_cliente=payload.es_cliente,
        es_proveedor=payload.es_proveedor,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedClienteProveedorResponse, summary='GET Cliente Proveedor', description='Obtener lista de clientes/proveedores con paginación.')
def list_cliente_proveedor(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(ClienteProveedor).count()
    
    # Obtener elementos de la página actual
    items = db.query(ClienteProveedor).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ClienteProveedorRead, summary='GET Cliente Proveedor', description='GET Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def get_cliente_proveedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")
    return item


@router.put("/{item_id}", response_model=ClienteProveedorRead, summary='PUT Cliente Proveedor', description='PUT Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def update_cliente_proveedor(
    item_id: int, payload: ClienteProveedorUpdate, db: Session = Depends(get_db)
):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Cliente Proveedor', description='DELETE Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def delete_cliente_proveedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
