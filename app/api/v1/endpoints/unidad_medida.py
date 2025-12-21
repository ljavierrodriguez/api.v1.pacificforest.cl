from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.unidad_medida import UnidadMedida
from app.schemas.unidad_medida import UnidadMedidaCreate, UnidadMedidaRead, UnidadMedidaUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/unidad_medida", tags=["unidad_medida"])


@router.post("/", response_model=UnidadMedidaRead, status_code=201, summary='POST UnidadMedida', description='Crear una nueva unidad de medida.')
def create_unidad_medida(payload: UnidadMedidaCreate, db: Session = Depends(get_db)):
    obj = UnidadMedida(
        nombre=payload.nombre,
        equivalencia_mm=payload.equivalencia_mm,
        descripcion=payload.descripcion,
        por_defecto=payload.por_defecto,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET UnidadMedida', description='Obtener lista de unidades de medida con paginación.')
def list_unidad_medida(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(UnidadMedida).count()
    
    # Obtener elementos de la página actual
    items = db.query(UnidadMedida).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=UnidadMedidaRead, summary='GET UnidadMedida', description='Obtener una unidad de medida específica por ID.')
def get_unidad_medida(item_id: int, db: Session = Depends(get_db)):
    item = db.get(UnidadMedida, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="UnidadMedida not found")
    return item


@router.put("/{item_id}", response_model=UnidadMedidaRead, summary='PUT UnidadMedida', description='Actualizar una unidad de medida existente.')
def update_unidad_medida(item_id: int, payload: UnidadMedidaUpdate, db: Session = Depends(get_db)):
    item = db.get(UnidadMedida, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="UnidadMedida not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE UnidadMedida', description='Eliminar una unidad de medida.')
def delete_unidad_medida(item_id: int, db: Session = Depends(get_db)):
    item = db.get(UnidadMedida, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="UnidadMedida not found")
    db.delete(item)
    db.commit()
    return {"ok": True}