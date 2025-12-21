from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.ide import Ide
from app.schemas.ide import IdeCreate, IdeRead, IdeUpdate
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/ide", tags=["ide"])


@router.post("/", response_model=IdeRead, summary='POST Ide', description='POST Ide endpoint. Replace this placeholder with a meaningful description.')
def create_ide(payload: IdeCreate, db: Session = Depends(get_db)):
    obj = Ide(
        id_proforma=payload.id_proforma,
        id_tipo_envase=payload.id_tipo_envase,
        referencia=payload.referencia,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", summary='GET Ide', description='GET Ide endpoint. Replace this placeholder with a meaningful description.')
def list_ide(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Ide).count()
    
    # Obtener elementos de la página actual
    items = db.query(Ide).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=IdeRead, summary='GET Ide', description='GET Ide endpoint. Replace this placeholder with a meaningful description.')
def get_ide(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ide, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ide not found")
    return item


@router.put("/{item_id}", response_model=IdeRead, summary='PUT Ide', description='PUT Ide endpoint. Replace this placeholder with a meaningful description.')
def update_ide(item_id: int, payload: IdeUpdate, db: Session = Depends(get_db)):
    item = db.get(Ide, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ide not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Ide', description='DELETE Ide endpoint. Replace this placeholder with a meaningful description.')
def delete_ide(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ide, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ide not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
