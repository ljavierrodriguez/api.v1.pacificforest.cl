from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.gasto import Gasto
from app.schemas.gasto import GastoCreate, GastoRead, GastoUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/gasto", tags=["gasto"])


@router.post("/", response_model=GastoRead, summary='POST Gasto', description='POST Gasto endpoint. Replace this placeholder with a meaningful description.')
def create_gasto(payload: GastoCreate, db: Session = Depends(get_db)):
    obj = Gasto(descripcion=payload.descripcion, monto=payload.monto)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Gasto', description='GET Gasto endpoint. Replace this placeholder with a meaningful description.')
def list_gasto(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Gasto).count()
    
    # Obtener elementos de la página actual
    items = db.query(Gasto).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=GastoRead, summary='GET Gasto', description='GET Gasto endpoint. Replace this placeholder with a meaningful description.')
def get_gasto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Gasto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Gasto not found")
    return item


@router.put("/{item_id}", response_model=GastoRead, summary='PUT Gasto', description='PUT Gasto endpoint. Replace this placeholder with a meaningful description.')
def update_gasto(item_id: int, payload: GastoUpdate, db: Session = Depends(get_db)):
    item = db.get(Gasto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Gasto not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Gasto', description='DELETE Gasto endpoint. Replace this placeholder with a meaningful description.')
def delete_gasto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Gasto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Gasto not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
