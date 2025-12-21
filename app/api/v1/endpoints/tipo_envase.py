from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.tipo_envase import TipoEnvase
from app.schemas.tipo_envase import TipoEnvaseCreate, TipoEnvaseRead, TipoEnvaseUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/tipo_envase", tags=["tipo_envase"])


@router.post("/", response_model=TipoEnvaseRead, summary='POST Tipo Envase', description='POST Tipo Envase endpoint. Replace this placeholder with a meaningful description.')
def create_tipo_envase(payload: TipoEnvaseCreate, db: Session = Depends(get_db)):
    obj = TipoEnvase(nombre=payload.nombre)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Tipo Envase', description='GET Tipo Envase endpoint. Replace this placeholder with a meaningful description.')
def list_tipo_envase(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(TipoEnvase).count()
    
    # Obtener elementos de la página actual
    items = db.query(TipoEnvase).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=TipoEnvaseRead, summary='GET Tipo Envase', description='GET Tipo Envase endpoint. Replace this placeholder with a meaningful description.')
def get_tipo_envase(item_id: int, db: Session = Depends(get_db)):
    item = db.get(TipoEnvase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="TipoEnvase not found")
    return item


@router.put("/{item_id}", response_model=TipoEnvaseRead, summary='PUT Tipo Envase', description='PUT Tipo Envase endpoint. Replace this placeholder with a meaningful description.')
def update_tipo_envase(item_id: int, payload: TipoEnvaseUpdate, db: Session = Depends(get_db)):
    item = db.get(TipoEnvase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="TipoEnvase not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Tipo Envase', description='DELETE Tipo Envase endpoint. Replace this placeholder with a meaningful description.')
def delete_tipo_envase(item_id: int, db: Session = Depends(get_db)):
    item = db.get(TipoEnvase, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="TipoEnvase not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
