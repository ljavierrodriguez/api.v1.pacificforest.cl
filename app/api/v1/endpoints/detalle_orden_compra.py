from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, cast, Numeric
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal, InvalidOperation

from app.db.session import get_db
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.detalle_proforma import DetalleProforma
from app.models.especie import Especie
from app.models.orden_compra import OrdenCompra
from app.models.producto import Producto
from app.models.proforma import Proforma
from app.schemas.detalle_orden_compra import (
DetalleOrdenCompraCreate,
    DetalleOrdenCompraRead,
    DetalleOrdenCompraUpdate,
)
from app.schemas.pagination import create_paginated_response

from app.api.v1.endpoints.orden_compra import _validate_volumen_orden_vs_proforma, _is_directa

router = APIRouter(prefix="/detalle_orden_compra", tags=["detalle_orden_compra"])


VOLUME_EPSILON = Decimal("0.001")
VOLUME_TOLERANCE_PCT = Decimal("0.10")


def _to_decimal(val) -> Decimal:
    if val is None:
        return Decimal("0")
    try:
        return Decimal(str(val))
    except Exception:
        return Decimal("0")


def _validate_producto_vs_proforma(db: Session, proforma_id: int, producto_id: int | None) -> None:
    if not producto_id:
        return

    productos_proforma = {
        pid
        for (pid,) in (
            db.query(DetalleProforma.id_producto)
            .filter(DetalleProforma.id_proforma == proforma_id)
            .distinct()
            .all()
        )
        if pid is not None
    }

    if productos_proforma and producto_id not in productos_proforma:
        raise HTTPException(
            status_code=403,
            detail=f"El producto con ID {producto_id} no pertenece a la proforma seleccionada",
        )


def _update_proforma_estado(db: Session, id_proforma: int) -> None:
    proforma = db.get(Proforma, id_proforma)
    if not proforma:
        return

    volumen_proforma = db.query(
        func.coalesce(func.sum(DetalleProforma.volumen_eq), 0)
    ).filter(DetalleProforma.id_proforma == id_proforma).scalar()

    volumen_odc = db.query(
        func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
    ).join(
        OrdenCompra,
        DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
    ).filter(
        OrdenCompra.id_proforma == id_proforma,
        func.coalesce(OrdenCompra.vinculado, 0) != 1,
    ).scalar()

    if (volumen_odc or 0) == 0:
        proforma.id_estado_proforma = 1
    elif (volumen_odc or 0) >= (volumen_proforma or 0) - 10:
        proforma.id_estado_proforma = 3
    else:
        proforma.id_estado_proforma = 2


@router.post("/", response_model=DetalleOrdenCompraRead, summary='POST Detalle Orden Compra', description='POST Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def create_detalle(payload: DetalleOrdenCompraCreate, db: Session = Depends(get_db)):
    orden = db.get(OrdenCompra, payload.id_orden_compra)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

    if orden.id_proforma:
        _validate_producto_vs_proforma(db, orden.id_proforma, payload.id_producto)

    obj = DetalleOrdenCompra(**payload.model_dump())
    db.add(obj)
    db.flush()

    if orden.id_proforma and not _is_directa(orden.vinculado):
        _validate_volumen_orden_vs_proforma(db, orden.id_proforma, orden.id_orden_compra)

    db.commit()
    db.refresh(obj)
    if orden.id_proforma:
        _update_proforma_estado(db, orden.id_proforma)
        db.commit()
    return obj


@router.get("/", summary='GET Detalle Orden Compra', description='Listar todos los detalles de orden de compra paginados.')
def list_detalles(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=1000, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    query = db.query(DetalleOrdenCompra)
    total_items = query.count()
    items = query.offset(skip).limit(page_size).all()
    return create_paginated_response(items, page, page_size, total_items)


# Nuevo endpoint para filtrar por orden de compra
@router.get("/by-orden/{id_orden_compra}", summary='GET Detalles por Orden de Compra', description='Listar detalles de una orden de compra específica, paginados.')
def list_detalles_by_orden(
    id_orden_compra: int,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=1000, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    base_query = db.query(DetalleOrdenCompra).filter(
        DetalleOrdenCompra.id_orden_compra == id_orden_compra
    )
    total_items = base_query.count()

    rows = db.query(
        DetalleOrdenCompra,
        Producto.nombre_producto_esp.label("producto_nombre"),
        Producto.id_especie.label("id_especie"),
        Especie.nombre_esp.label("especie_nombre"),
    ).outerjoin(
        Producto,
        DetalleOrdenCompra.id_producto == Producto.id_producto,
    ).outerjoin(
        Especie,
        Producto.id_especie == Especie.id_especie,
    ).filter(
        DetalleOrdenCompra.id_orden_compra == id_orden_compra
    ).offset(skip).limit(page_size).all()

    items = []
    for detalle, producto_nombre, id_especie, especie_nombre in rows:
        item_dict = detalle.to_dict() if hasattr(detalle, "to_dict") else dict(detalle.__dict__)
        if item_dict.get("volumen") is not None:
            item_dict["volumen"] = f"{float(item_dict['volumen']):.2f}"
        if item_dict.get("volumen_eq") is not None:
            item_dict["volumen_eq"] = f"{float(item_dict['volumen_eq']):.2f}"
        item_dict["producto_nombre"] = producto_nombre
        item_dict["id_especie"] = id_especie
        item_dict["especie_nombre"] = especie_nombre
        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=DetalleOrdenCompraRead, summary='GET Detalle Orden Compra', description='GET Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def get_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=DetalleOrdenCompraRead, summary='PUT Detalle Orden Compra', description='PUT Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def update_detalle(item_id: int, payload: DetalleOrdenCompraUpdate, db: Session = Depends(get_db)):
    item = db.get(DetalleOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    orden = db.get(OrdenCompra, item.id_orden_compra)
    new_id_producto = payload.id_producto if payload.id_producto is not None else item.id_producto

    if orden and orden.id_proforma:
        _validate_producto_vs_proforma(db, orden.id_proforma, new_id_producto)

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.flush()

    if orden and orden.id_proforma and not _is_directa(orden.vinculado):
        _validate_volumen_orden_vs_proforma(db, orden.id_proforma, orden.id_orden_compra)

    db.commit()
    db.refresh(item)
    if orden and orden.id_proforma:
        _update_proforma_estado(db, orden.id_proforma)
        db.commit()
    return item


@router.delete("/{item_id}", summary='DELETE Detalle Orden Compra', description='DELETE Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def delete_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleOrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    orden = db.get(OrdenCompra, item.id_orden_compra)
    proforma_id = orden.id_proforma if orden else None
    db.delete(item)
    db.commit()
    if proforma_id:
        _update_proforma_estado(db, proforma_id)
        db.commit()
    return {"ok": True}
