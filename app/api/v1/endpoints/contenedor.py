from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.contenedor import Contenedor
from app.schemas.contenedor import ContenedorCreate, ContenedorRead, ContenedorUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/contenedor", tags=["contenedor"])


@router.post("/", response_model=ContenedorRead, summary='POST Contenedor', description='POST Contenedor endpoint. Replace this placeholder with a meaningful description.')
def create_contenedor(payload: ContenedorCreate, db: Session = Depends(get_db)):
    obj = Contenedor(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Contenedor', description='GET Contenedor endpoint. Replace this placeholder with a meaningful description.')
def list_contenedores(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Contenedor).count()
    
    # Obtener elementos de la página actual
    items = db.query(Contenedor).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ContenedorRead, summary='GET Contenedor', description='GET Contenedor endpoint. Replace this placeholder with a meaningful description.')
def get_contenedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Contenedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=ContenedorRead, summary='PUT Contenedor', description='PUT Contenedor endpoint. Replace this placeholder with a meaningful description.')
def update_contenedor(item_id: int, payload: ContenedorUpdate, db: Session = Depends(get_db)):
    item = db.get(Contenedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Contenedor', description='DELETE Contenedor endpoint. Replace this placeholder with a meaningful description.')
def delete_contenedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Contenedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
