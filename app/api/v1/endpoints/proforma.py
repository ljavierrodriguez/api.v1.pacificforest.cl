from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.proforma import Proforma
from app.schemas.proforma import ProformaCreate, ProformaRead, ProformaUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para Proforma
PaginatedProformaResponse = create_paginated_response_model(ProformaRead)

router = APIRouter(prefix="/proforma", tags=["proforma"])


@router.post("/", response_model=ProformaRead, status_code=201, summary='POST Proforma', description='Crear una nueva proforma.')
def create_proforma(payload: ProformaCreate, db: Session = Depends(get_db)):
    obj = Proforma(
        id_operacion_exportacion=payload.id_operacion_exportacion,
        id_contenedor=payload.id_contenedor,
        id_usuario_encargado=payload.id_usuario_encargado,
        id_estado_proforma=payload.id_estado_proforma,
        id_moneda=payload.id_moneda,
        id_agente=payload.id_agente,
        id_tipo_comision=payload.id_tipo_comision,
        id_clausula_venta=payload.id_clausula_venta,
        #id_forma_pago=payload.id_forma_pago,
        cantidad_contenedor=payload.cantidad_contenedor,
        fecha_emision=payload.fecha_emision,
        fecha_aceptacion=payload.fecha_aceptacion,
        fecha_entrega=payload.fecha_entrega,
        valor_flete=payload.valor_flete,
        especificaciones=payload.especificaciones,
        nota=payload.nota,
        nota_1=payload.nota_1,
        nota_2=payload.nota_2,
        url_imagen=payload.url_imagen,
        id_empresa=payload.id_empresa,
        id_direccion_facturar=payload.id_direccion_facturar,
        id_direccion_consignar=payload.id_direccion_consignar,
        id_direccion_notificar=payload.id_direccion_notificar,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedProformaResponse, summary='GET Proforma', description='Obtener lista de proformas con paginación.')
def list_proforma(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Proforma).count()
    
    # Obtener elementos de la página actual
    items = db.query(Proforma).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ProformaRead, summary='GET Proforma', description='Obtener una proforma específica por ID.')
def get_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    return item


@router.put("/{item_id}", response_model=ProformaRead, summary='PUT Proforma', description='Actualizar una proforma existente.')
def update_proforma(item_id: int, payload: ProformaUpdate, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Proforma', description='Eliminar una proforma.')
def delete_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    
    # Verificar si tiene órdenes de compra asociadas
    ordenes_actuales = item.OrdenesCompra.count()
    ordenes_anteriores = item.OrdenesCompraAnterior.count()
    
    if ordenes_actuales > 0 or ordenes_anteriores > 0:
        total_ordenes = ordenes_actuales + ordenes_anteriores
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la proforma porque tiene {total_ordenes} orden(es) de compra asociada(s)"
        )
    
    # Verificar si tiene detalles de proforma
    detalles_count = item.DetalleProforma.count()
    if detalles_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la proforma porque tiene {detalles_count} detalle(s) asociado(s)"
        )
    
    # Verificar si tiene contactos de proforma
    contactos_count = item.ContactosProforma.count()
    if contactos_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la proforma porque tiene {contactos_count} contacto(s) asociado(s)"
        )
    
    db.delete(item)
    db.commit()
    return {"ok": True}
