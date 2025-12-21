from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.operacion_exportacion import OperacionExportacion
from app.schemas.operacion_exportacion import (
OperacionExportacionCreate,
    OperacionExportacionRead,
    OperacionExportacionUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/operacion_exportacion", tags=["operacion_exportacion"])


@router.post("/", response_model=OperacionExportacionRead, summary='POST Operacion Exportacion', description='POST Operacion Exportacion endpoint. Replace this placeholder with a meaningful description.')
def create_operacion(payload: OperacionExportacionCreate, db: Session = Depends(get_db)):
    obj = OperacionExportacion(referencia=payload.referencia, fecha_operacion=payload.fecha_operacion)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Operacion Exportacion', description='GET Operacion Exportacion endpoint. Replace this placeholder with a meaningful description.')
def list_operacion(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(OperacionExportacion).count()
    
    # Obtener elementos de la página actual
    items = db.query(OperacionExportacion).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=OperacionExportacionRead, summary='GET Operacion Exportacion', description='GET Operacion Exportacion endpoint. Replace this placeholder with a meaningful description.')
def get_operacion(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OperacionExportacion, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OperacionExportacion not found")
    return item


@router.put("/{item_id}", response_model=OperacionExportacionRead, summary='PUT Operacion Exportacion', description='PUT Operacion Exportacion endpoint. Replace this placeholder with a meaningful description.')
def update_operacion(item_id: int, payload: OperacionExportacionUpdate, db: Session = Depends(get_db)):
    item = db.get(OperacionExportacion, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OperacionExportacion not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Operacion Exportacion', description='DELETE Operacion Exportacion endpoint. Replace this placeholder with a meaningful description.')
def delete_operacion(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OperacionExportacion, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OperacionExportacion not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
