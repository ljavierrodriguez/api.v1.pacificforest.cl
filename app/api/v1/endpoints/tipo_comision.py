from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.tipo_comision import TipoComision
from app.schemas.tipo_comision import TipoComisionCreate, TipoComisionRead, TipoComisionUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/tipo_comision", tags=["tipo_comision"])


@router.post("/", response_model=TipoComisionRead, status_code=201, summary='POST TipoComision', description='Crear un nuevo tipo de comisión.')
def create_tipo_comision(payload: TipoComisionCreate, db: Session = Depends(get_db)):
    obj = TipoComision(
        nombre=payload.nombre,
        por_defecto=payload.por_defecto,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET TipoComision', description='Obtener lista de tipos de comisión con paginación.')
def list_tipo_comision(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(TipoComision).count()
    
    # Obtener elementos de la página actual
    items = db.query(TipoComision).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=TipoComisionRead, summary='GET TipoComision', description='Obtener un tipo de comisión específico por ID.')
def get_tipo_comision(item_id: int, db: Session = Depends(get_db)):
    item = db.get(TipoComision, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="TipoComision not found")
    return item


@router.put("/{item_id}", response_model=TipoComisionRead, summary='PUT TipoComision', description='Actualizar un tipo de comisión existente.')
def update_tipo_comision(item_id: int, payload: TipoComisionUpdate, db: Session = Depends(get_db)):
    item = db.get(TipoComision, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="TipoComision not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE TipoComision', description='Eliminar un tipo de comisión.')
def delete_tipo_comision(item_id: int, db: Session = Depends(get_db)):
    item = db.get(TipoComision, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="TipoComision not found")
    db.delete(item)
    db.commit()
    return {"ok": True}