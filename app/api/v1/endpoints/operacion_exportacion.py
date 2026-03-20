from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, or_
from typing import List

from app.db.session import get_db
from app.models.cliente_proveedor import ClienteProveedor
from app.models.operacion_exportacion import OperacionExportacion
from app.models.puerto import Puerto
from app.schemas.operacion_exportacion import (
OperacionExportacionCreate,
    OperacionExportacionRead,
    OperacionExportacionUpdate,
)
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para OperacionExportacion
PaginatedOperacionExportacionResponse = create_paginated_response_model(OperacionExportacionRead)

router = APIRouter(prefix="/operacion_exportacion", tags=["operacion_exportacion"])


@router.post("/", response_model=OperacionExportacionRead, status_code=201, summary='POST Operacion Exportacion', description='Crear una nueva operación de exportación.')
def create_operacion(payload: OperacionExportacionCreate, db: Session = Depends(get_db)):
    obj = OperacionExportacion(
        facturar_a=payload.facturar_a,
        consignar_a=payload.consignar_a,
        notificar_a=payload.notificar_a,
        id_puerto_origen=payload.id_puerto_origen,
        id_puerto_destino=payload.id_puerto_destino,
        id_forma_pago=payload.id_forma_pago,
        id_estado_oe=payload.id_estado_oe,
        fecha=payload.fecha
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedOperacionExportacionResponse, summary='GET Operacion Exportacion', description='Obtener lista de operaciones de exportación con paginación.')
def list_operacion(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(OperacionExportacion).count()
    
    # Obtener elementos de la página actual, desde la más reciente
    items = (
        db.query(OperacionExportacion)
        .order_by(desc(OperacionExportacion.fecha), desc(OperacionExportacion.id_operacion_exportacion))
        .offset(skip)
        .limit(page_size)
        .all()
    )
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/search", response_model=PaginatedOperacionExportacionResponse, summary='SEARCH Operacion Exportacion', description='Buscar operaciones de exportación por clientes o puertos con paginación.')
def search_operacion(
    q: str | None = Query(None, description="Texto global para buscar en clientes o puertos"),
    facturar_q: str | None = Query(None, description="Buscar por cliente de facturación"),
    consignar_q: str | None = Query(None, description="Buscar por cliente de consignación"),
    notificar_q: str | None = Query(None, description="Buscar por cliente de notificación"),
    puerto_origen_q: str | None = Query(None, description="Buscar por puerto de origen"),
    puerto_destino_q: str | None = Query(None, description="Buscar por puerto de destino"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size

    facturar_cliente = aliased(ClienteProveedor)
    consignar_cliente = aliased(ClienteProveedor)
    notificar_cliente = aliased(ClienteProveedor)
    puerto_origen = aliased(Puerto)
    puerto_destino = aliased(Puerto)

    query = (
        db.query(OperacionExportacion)
        .join(facturar_cliente, OperacionExportacion.facturar_a == facturar_cliente.id_cliente_proveedor)
        .join(consignar_cliente, OperacionExportacion.consignar_a == consignar_cliente.id_cliente_proveedor)
        .join(notificar_cliente, OperacionExportacion.notificar_a == notificar_cliente.id_cliente_proveedor)
        .join(puerto_origen, OperacionExportacion.id_puerto_origen == puerto_origen.id_puerto)
        .outerjoin(puerto_destino, OperacionExportacion.id_puerto_destino == puerto_destino.id_puerto)
    )

    def _contains(value: str | None):
        return f"%{value.strip()}%" if value and value.strip() else None

    search_global = _contains(q)
    if search_global:
        query = query.filter(
            or_(
                facturar_cliente.nombre_fantasia.ilike(search_global),
                facturar_cliente.razon_social.ilike(search_global),
                consignar_cliente.nombre_fantasia.ilike(search_global),
                consignar_cliente.razon_social.ilike(search_global),
                notificar_cliente.nombre_fantasia.ilike(search_global),
                notificar_cliente.razon_social.ilike(search_global),
                puerto_origen.nombre.ilike(search_global),
                puerto_destino.nombre.ilike(search_global),
            )
        )

    search_facturar = _contains(facturar_q)
    if search_facturar:
        query = query.filter(
            or_(
                facturar_cliente.nombre_fantasia.ilike(search_facturar),
                facturar_cliente.razon_social.ilike(search_facturar),
            )
        )

    search_consignar = _contains(consignar_q)
    if search_consignar:
        query = query.filter(
            or_(
                consignar_cliente.nombre_fantasia.ilike(search_consignar),
                consignar_cliente.razon_social.ilike(search_consignar),
            )
        )

    search_notificar = _contains(notificar_q)
    if search_notificar:
        query = query.filter(
            or_(
                notificar_cliente.nombre_fantasia.ilike(search_notificar),
                notificar_cliente.razon_social.ilike(search_notificar),
            )
        )

    search_puerto_origen = _contains(puerto_origen_q)
    if search_puerto_origen:
        query = query.filter(puerto_origen.nombre.ilike(search_puerto_origen))

    search_puerto_destino = _contains(puerto_destino_q)
    if search_puerto_destino:
        query = query.filter(puerto_destino.nombre.ilike(search_puerto_destino))

    # Obtener total de elementos filtrados
    total_items = query.count()

    # Obtener elementos de la página actual, desde la más reciente
    items = (
        query
        .order_by(desc(OperacionExportacion.fecha), desc(OperacionExportacion.id_operacion_exportacion))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=OperacionExportacionRead, summary='GET Operacion Exportacion', description='Obtener una operación de exportación específica por ID.')
def get_operacion(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OperacionExportacion, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OperacionExportacion not found")
    return item


@router.put("/{item_id}", response_model=OperacionExportacionRead, summary='PUT Operacion Exportacion', description='Actualizar una operación de exportación existente.')
def update_operacion(item_id: int, payload: OperacionExportacionUpdate, db: Session = Depends(get_db)):
    item = db.get(OperacionExportacion, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OperacionExportacion not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Operacion Exportacion', description='Eliminar una operación de exportación.')
def delete_operacion(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OperacionExportacion, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OperacionExportacion not found")
    
    # Validar que no exista una proforma asociada
    if item.Proforma:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar una operación de exportación que tiene una proforma asociada"
        )
    
    db.delete(item)
    db.commit()
    return {"ok": True}
