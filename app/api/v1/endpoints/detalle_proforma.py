from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.detalle_proforma import DetalleProforma
from app.schemas.detalle_proforma import (
DetalleProformaCreate,
    DetalleProformaRead,
    DetalleProformaUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/detalle_proforma", tags=["detalle_proforma"])


@router.post("/", response_model=DetalleProformaRead, summary='POST Detalle Proforma', description='POST Detalle Proforma endpoint. Replace this placeholder with a meaningful description.')
def create_detalle_proforma(payload: DetalleProformaCreate, db: Session = Depends(get_db)):
    obj = DetalleProforma(
        id_proforma=payload.id_proforma,
        id_producto=payload.id_producto,
        id_unidad_venta=payload.id_unidad_venta,
        cantidad=payload.cantidad,
        precio_unitario=payload.precio_unitario,
        subtotal=payload.subtotal,
        volumen_eq=payload.volumen_eq,
        precio_eq=payload.precio_eq,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Detalle Proforma', description='GET Detalle Proforma endpoint. Replace this placeholder with a meaningful description.')
def list_detalle_proforma(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(DetalleProforma).count()
    
    # Obtener elementos de la página actual
    items = db.query(DetalleProforma).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=DetalleProformaRead, summary='GET Detalle Proforma', description='GET Detalle Proforma endpoint. Replace this placeholder with a meaningful description.')
def get_detalle_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DetalleProforma not found")
    return item


@router.put("/{item_id}", response_model=DetalleProformaRead, summary='PUT Detalle Proforma', description='PUT Detalle Proforma endpoint. Replace this placeholder with a meaningful description.')
def update_detalle_proforma(item_id: int, payload: DetalleProformaUpdate, db: Session = Depends(get_db)):
    item = db.get(DetalleProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DetalleProforma not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Detalle Proforma', description='DELETE Detalle Proforma endpoint. Replace this placeholder with a meaningful description.')
def delete_detalle_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DetalleProforma not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
