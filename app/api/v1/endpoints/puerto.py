from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.puerto import Puerto
from app.schemas.puerto import PuertoCreate, PuertoRead, PuertoUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/puerto", tags=["puerto"])


@router.post("/", response_model=PuertoRead, summary='POST Puerto', description='POST Puerto endpoint. Replace this placeholder with a meaningful description.')
def create_puerto(payload: PuertoCreate, db: Session = Depends(get_db)):
    obj = Puerto(nombre=payload.nombre, codigo=payload.codigo)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Puerto', description='GET Puerto endpoint. Replace this placeholder with a meaningful description.')
def list_puerto(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Puerto).count()
    
    # Obtener elementos de la página actual
    items = db.query(Puerto).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=PuertoRead, summary='GET Puerto', description='GET Puerto endpoint. Replace this placeholder with a meaningful description.')
def get_puerto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Puerto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Puerto not found")
    return item


@router.put("/{item_id}", response_model=PuertoRead, summary='PUT Puerto', description='PUT Puerto endpoint. Replace this placeholder with a meaningful description.')
def update_puerto(item_id: int, payload: PuertoUpdate, db: Session = Depends(get_db)):
    item = db.get(Puerto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Puerto not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Puerto', description='DELETE Puerto endpoint. Replace this placeholder with a meaningful description.')
def delete_puerto(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Puerto, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Puerto not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
