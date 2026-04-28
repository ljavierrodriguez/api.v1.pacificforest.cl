from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, or_
from typing import List

from app.db.session import get_db
from app.models.cliente_proveedor import ClienteProveedor
from app.models.estado_oe import EstadoOe
from app.models.forma_pago import FormaPago
from app.models.operacion_exportacion import OperacionExportacion
from app.models.proforma import Proforma
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


def _build_oe_query(db: Session):
    """Construye la query base con todos los joins para enriquecer la respuesta."""
    FacturarCP = aliased(ClienteProveedor)
    ConsignarCP = aliased(ClienteProveedor)
    NotificarCP = aliased(ClienteProveedor)
    PuertoOrigen = aliased(Puerto)
    PuertoDestino = aliased(Puerto)

    return (
        db.query(
            OperacionExportacion,
            Proforma.id_proforma,
            FacturarCP.razon_social.label("facturar_a_nombre"),
            ConsignarCP.razon_social.label("consignar_a_nombre"),
            NotificarCP.razon_social.label("notificar_a_nombre"),
            PuertoOrigen.nombre.label("puerto_origen_nombre"),
            PuertoDestino.nombre.label("puerto_destino_nombre"),
            FormaPago.nombre.label("forma_pago_nombre"),
            EstadoOe.nombre.label("estado_oe_nombre"),
        )
        .outerjoin(Proforma, Proforma.id_operacion_exportacion == OperacionExportacion.id_operacion_exportacion)
        .outerjoin(FacturarCP, OperacionExportacion.facturar_a == FacturarCP.id_cliente_proveedor)
        .outerjoin(ConsignarCP, OperacionExportacion.consignar_a == ConsignarCP.id_cliente_proveedor)
        .outerjoin(NotificarCP, OperacionExportacion.notificar_a == NotificarCP.id_cliente_proveedor)
        .outerjoin(PuertoOrigen, OperacionExportacion.id_puerto_origen == PuertoOrigen.id_puerto)
        .outerjoin(PuertoDestino, OperacionExportacion.id_puerto_destino == PuertoDestino.id_puerto)
        .outerjoin(FormaPago, OperacionExportacion.id_forma_pago == FormaPago.id_forma_pago)
        .outerjoin(EstadoOe, OperacionExportacion.id_estado_oe == EstadoOe.id_estado_oe),
        FacturarCP, ConsignarCP, NotificarCP, PuertoOrigen, PuertoDestino
    )


def _rows_to_items(rows):
    items = []
    for row in rows:
        oe = row[0]
        d = oe.__dict__.copy()
        d.update({
            "id_proforma": row[1],
            "facturar_a_nombre": row[2],
            "consignar_a_nombre": row[3],
            "notificar_a_nombre": row[4],
            "puerto_origen_nombre": row[5],
            "puerto_destino_nombre": row[6],
            "forma_pago_nombre": row[7],
            "estado_oe_nombre": row[8],
        })
        items.append(d)
    return items


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
    skip = (page - 1) * page_size
    total_items = db.query(OperacionExportacion).count()

    base_query, *_ = _build_oe_query(db)
    rows = (
        base_query
        .order_by(desc(OperacionExportacion.id_operacion_exportacion))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    return create_paginated_response(_rows_to_items(rows), page, page_size, total_items)


@router.get("/search", response_model=PaginatedOperacionExportacionResponse, summary='SEARCH Operacion Exportacion', description='Buscar operaciones de exportación por clientes o puertos con paginación.')
def search_operacion(
    oe_id: int | None = Query(None, ge=1, description="Buscar por número de OE (ID de operación)"),
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
    skip = (page - 1) * page_size

    base_query, FacturarCP, ConsignarCP, NotificarCP, PuertoOrigen, PuertoDestino = _build_oe_query(db)

    if oe_id is not None:
        base_query = base_query.filter(OperacionExportacion.id_operacion_exportacion == oe_id)

    def _contains(value: str | None):
        return f"%{value.strip()}%" if value and value.strip() else None

    search_global = _contains(q)
    if search_global:
        base_query = base_query.filter(
            or_(
                FacturarCP.nombre_fantasia.ilike(search_global),
                FacturarCP.razon_social.ilike(search_global),
                ConsignarCP.nombre_fantasia.ilike(search_global),
                ConsignarCP.razon_social.ilike(search_global),
                NotificarCP.nombre_fantasia.ilike(search_global),
                NotificarCP.razon_social.ilike(search_global),
                PuertoOrigen.nombre.ilike(search_global),
                PuertoDestino.nombre.ilike(search_global),
            )
        )

    search_facturar = _contains(facturar_q)
    if search_facturar:
        base_query = base_query.filter(
            or_(
                FacturarCP.nombre_fantasia.ilike(search_facturar),
                FacturarCP.razon_social.ilike(search_facturar),
            )
        )

    search_consignar = _contains(consignar_q)
    if search_consignar:
        base_query = base_query.filter(
            or_(
                ConsignarCP.nombre_fantasia.ilike(search_consignar),
                ConsignarCP.razon_social.ilike(search_consignar),
            )
        )

    search_notificar = _contains(notificar_q)
    if search_notificar:
        base_query = base_query.filter(
            or_(
                NotificarCP.nombre_fantasia.ilike(search_notificar),
                NotificarCP.razon_social.ilike(search_notificar),
            )
        )

    search_puerto_origen = _contains(puerto_origen_q)
    if search_puerto_origen:
        base_query = base_query.filter(PuertoOrigen.nombre.ilike(search_puerto_origen))

    search_puerto_destino = _contains(puerto_destino_q)
    if search_puerto_destino:
        base_query = base_query.filter(PuertoDestino.nombre.ilike(search_puerto_destino))

    total_items = base_query.count()

    rows = (
        base_query
        .order_by(desc(OperacionExportacion.id_operacion_exportacion))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    return create_paginated_response(_rows_to_items(rows), page, page_size, total_items)


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
