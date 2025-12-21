from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.naviera import Naviera
from app.schemas.naviera import NavieraCreate, NavieraRead, NavieraUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/naviera", tags=["naviera"])


@router.post("/", response_model=NavieraRead, status_code=201, summary='POST Naviera', description='Crear una nueva naviera.')
def create_naviera(payload: NavieraCreate, db: Session = Depends(get_db)):
    obj = Naviera(
        nombre=payload.nombre,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Naviera', description='Obtener lista de navieras con paginación.')
def list_naviera(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Naviera).count()
    
    # Obtener elementos de la página actual
    items = db.query(Naviera).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=NavieraRead, summary='GET Naviera', description='Obtener una naviera específica por ID.')
def get_naviera(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Naviera, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Naviera not found")
    return item


@router.put("/{item_id}", response_model=NavieraRead, summary='PUT Naviera', description='Actualizar una naviera existente.')
def update_naviera(item_id: int, payload: NavieraUpdate, db: Session = Depends(get_db)):
    item = db.get(Naviera, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Naviera not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Naviera', description='Eliminar una naviera.')
def delete_naviera(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Naviera, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Naviera not found")
    try:
        db.delete(item)
        db.commit()
        return {"ok": True}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))