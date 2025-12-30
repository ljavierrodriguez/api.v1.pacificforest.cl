from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaRead, EmpresaUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Empresa
PaginatedEmpresaResponse = create_paginated_response_model(EmpresaRead)

router = APIRouter(prefix="/empresa", tags=["empresa"])


@router.post("/", response_model=EmpresaRead, summary='POST Empresa', description='Crear una nueva empresa con todos los datos requeridos.')
def create_empresa(payload: EmpresaCreate, db: Session = Depends(get_db)):
    obj = Empresa(
        rut=payload.rut,
        nombre_fantasia=payload.nombre_fantasia,
        razon_social=payload.razon_social,
        direccion=payload.direccion,
        telefono_1=payload.telefono_1,
        telefono_2=payload.telefono_2,
        giro=payload.giro,
        id_ciudad=payload.id_ciudad,
        es_vigente=payload.es_vigente,
        en_proforma=payload.en_proforma,
        en_odc=payload.en_odc,
        por_defecto=payload.por_defecto,
        url_logo=payload.url_logo,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedEmpresaResponse, summary='GET Empresas', description='Obtener lista paginada de empresas.')
def list_empresa(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Empresa).count()
    
    # Obtener elementos de la página actual
    items = db.query(Empresa).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=EmpresaRead, summary='GET Empresa', description='Obtener una empresa específica por su ID.')
def get_empresa(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return item


@router.put("/{item_id}", response_model=EmpresaRead, summary='PUT Empresa', description='Actualizar una empresa existente.')
def update_empresa(item_id: int, payload: EmpresaUpdate, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Empresa', description='Eliminar una empresa por su ID.')
def delete_empresa(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    
    # No permitir eliminar la empresa por defecto
    if item.por_defecto:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar la empresa por defecto"
        )
    
    # Verificar si tiene proformas asociadas (necesito importar el modelo)
    from app.models.proforma import Proforma
    proformas_count = db.query(Proforma).filter(Proforma.id_empresa == item_id).count()
    
    if proformas_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la empresa porque tiene {proformas_count} proforma(s) asociada(s)"
        )
    
    db.delete(item)
    db.commit()
    return {"ok": True}
