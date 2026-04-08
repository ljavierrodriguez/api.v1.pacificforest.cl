from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Numeric, cast, func
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.detalle_proforma import DetalleProforma
from app.models.orden_compra import OrdenCompra
from app.models.proforma import Proforma
from app.schemas.detalle_orden_compra import (
DetalleOrdenCompraCreate,
    DetalleOrdenCompraRead,
    DetalleOrdenCompraUpdate,
)
from app.schemas.pagination import create_paginated_response

router = APIRouter(prefix="/detalle_orden_compra", tags=["detalle_orden_compra"])


def _validate_producto_vs_proforma(
    db: Session,
    proforma_id: int,
    id_producto: int | None,
) -> None:
    productos_proforma = {
        product_id
        for (product_id,) in (
            db.query(DetalleProforma.id_producto)
            .filter(DetalleProforma.id_proforma == proforma_id)
            .distinct()
            .all()
        )
        if product_id is not None
    }

    if not productos_proforma:
        if id_producto is not None:
            raise HTTPException(
                status_code=403,
                detail="La proforma asociada no tiene productos definidos; no se puede asignar id_producto en el detalle",
            )
        return

    if id_producto is None:
        raise HTTPException(
            status_code=403,
            detail="La proforma asociada tiene productos definidos; el detalle debe incluir id_producto",
        )

    if id_producto not in productos_proforma:
        raise HTTPException(
            status_code=403,
            detail=f"El producto {id_producto} no existe en la proforma asociada",
        )


def _update_proforma_estado(db: Session, proforma_id: int) -> None:
    proforma = db.get(Proforma, proforma_id)
    if not proforma:
        return

    volumen_proforma = db.query(
        func.coalesce(
            func.sum(cast(DetalleProforma.volumen_eq, Numeric(12, 3))),
            0,
        )
    ).filter(DetalleProforma.id_proforma == proforma_id).scalar()

    volumen_odc = db.query(
        func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
    ).join(
        OrdenCompra,
        DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
    ).filter(OrdenCompra.id_proforma == proforma_id).scalar()

    tiene_odc = db.query(OrdenCompra.id_orden_compra).filter(
        OrdenCompra.id_proforma == proforma_id
    ).first() is not None

    if not tiene_odc:
        proforma.id_estado_proforma = 1
    elif (volumen_odc or 0) >= (volumen_proforma or 0) - 10:
        proforma.id_estado_proforma = 3
    else:
        proforma.id_estado_proforma = 2

    db.add(proforma)


@router.post("/", response_model=DetalleOrdenCompraRead, summary='POST Detalle Orden Compra', description='POST Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def create_detalle(payload: DetalleOrdenCompraCreate, db: Session = Depends(get_db)):
    orden = db.get(OrdenCompra, payload.id_orden_compra)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

    if orden.id_proforma:
        _validate_producto_vs_proforma(db, orden.id_proforma, payload.id_producto)

    if orden.id_proforma and payload.volumen_eq is not None:
        volumen_proforma_total = db.query(
            func.coalesce(
                func.sum(cast(DetalleProforma.volumen_eq, Numeric(12, 3))),
                0,
            )
        ).filter(
            DetalleProforma.id_proforma == orden.id_proforma,
        ).scalar()

        volumen_otros_odc_total = db.query(
            func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
        ).join(
            OrdenCompra,
            DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
        ).filter(
            OrdenCompra.id_proforma == orden.id_proforma,
            OrdenCompra.id_orden_compra != orden.id_orden_compra,
        ).scalar()

        volumen_actual_odc_total = db.query(
            func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
        ).filter(
            DetalleOrdenCompra.id_orden_compra == orden.id_orden_compra,
        ).scalar()

        nuevo_total_odc = (volumen_actual_odc_total or 0) + (payload.volumen_eq or 0)
        limite = (volumen_proforma_total or 0) - (volumen_otros_odc_total or 0)

        if nuevo_total_odc > limite:
            if (volumen_otros_odc_total or 0) >= (volumen_proforma_total or 0):
                raise HTTPException(
                    status_code=403,
                    detail="El volumen de la proforma ya fue completado",
                )
            maximo_volumen = limite
            raise HTTPException(
                status_code=403,
                detail=f"El volumen total supera el pendiente de la proforma ({maximo_volumen})",
            )

    obj = DetalleOrdenCompra(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    if orden.id_proforma:
        _update_proforma_estado(db, orden.id_proforma)
        db.commit()
    return obj


@router.get("/", summary='GET Detalle Orden Compra', description='GET Detalle Orden Compra endpoint. Replace this placeholder with a meaningful description.')
def list_detalles(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(DetalleOrdenCompra).count()
    
    # Obtener elementos de la página actual
    items = db.query(DetalleOrdenCompra).offset(skip).limit(page_size).all()
    
    # Crear respuesta paginada
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
    new_volumen_eq = payload.volumen_eq if payload.volumen_eq is not None else item.volumen_eq
    new_id_producto = payload.id_producto if payload.id_producto is not None else item.id_producto

    if orden and orden.id_proforma:
        _validate_producto_vs_proforma(db, orden.id_proforma, new_id_producto)

    if orden and orden.id_proforma and new_volumen_eq is not None:
        volumen_proforma_total = db.query(
            func.coalesce(
                func.sum(cast(DetalleProforma.volumen_eq, Numeric(12, 3))),
                0,
            )
        ).filter(
            DetalleProforma.id_proforma == orden.id_proforma,
        ).scalar()

        volumen_otros_odc_total = db.query(
            func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
        ).join(
            OrdenCompra,
            DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
        ).filter(
            OrdenCompra.id_proforma == orden.id_proforma,
            OrdenCompra.id_orden_compra != orden.id_orden_compra,
        ).scalar()

        volumen_actual_odc_total = db.query(
            func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
        ).filter(
            DetalleOrdenCompra.id_orden_compra == orden.id_orden_compra,
            DetalleOrdenCompra.id_detalle_odc != item_id,
        ).scalar()

        nuevo_total_odc = (volumen_actual_odc_total or 0) + (new_volumen_eq or 0)
        limite = (volumen_proforma_total or 0) - (volumen_otros_odc_total or 0)

        if nuevo_total_odc > limite:
            if (volumen_otros_odc_total or 0) >= (volumen_proforma_total or 0):
                raise HTTPException(
                    status_code=403,
                    detail="El volumen de la proforma ya fue completado",
                )
            maximo_volumen = limite
            raise HTTPException(
                status_code=403,
                detail=f"El volumen total supera el pendiente de la proforma ({maximo_volumen})",
            )

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
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
