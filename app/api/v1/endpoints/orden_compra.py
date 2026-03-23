from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from decimal import Decimal, InvalidOperation

from app.db.session import get_db
from app.dependencies.permissions import require_permission
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.detalle_proforma import DetalleProforma
from app.models.orden_compra import OrdenCompra
from app.schemas.orden_compra import OrdenCompraCreate, OrdenCompraRead, OrdenCompraUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para OrdenCompra
PaginatedOrdenCompraResponse = create_paginated_response_model(OrdenCompraRead)

router = APIRouter(prefix="/orden_compra", tags=["orden_compra"])


@router.post("/", response_model=OrdenCompraRead, status_code=201, summary='POST OrdenCompra', description='Crear una nueva orden de compra.', dependencies=[Depends(require_permission("orden_compra", "create"))])
def create_orden_compra(payload: OrdenCompraCreate, db: Session = Depends(get_db)):
    # Validar que detalles no esté vacío
    if not payload.detalles or len(payload.detalles) == 0:
        raise HTTPException(
            status_code=400,
            detail="La orden de compra debe tener al menos 1 detalle",
        )

    def _to_decimal(value) -> Decimal:
        if value is None:
            return Decimal("0")
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal("0")

    obj = OrdenCompra(
        id_proforma=payload.id_proforma,
        id_proforma_anterior=payload.id_proforma_anterior,
        fecha_emision=payload.fecha_emision,
        id_cliente_proveedor=payload.id_cliente_proveedor,
        id_usuario_encargado=payload.id_usuario_encargado,
        fecha_entrega=payload.fecha_entrega,
        id_bodega=payload.id_bodega,
        destino=payload.destino,
        id_moneda=payload.id_moneda,
        id_empresa=payload.id_empresa,
        ajustar_volumen=payload.ajustar_volumen,
        observacion=payload.observacion,
        id_usuario=payload.id_usuario,
        nota_1=payload.nota_1,
        otras_especificaciones=payload.otras_especificaciones,
        url_imagen=payload.url_imagen,
        valor_neto=payload.valor_neto,
        iva=payload.iva,
        tasa_iva=payload.tasa_iva,
        valor_total=payload.valor_total,
        id_estado_odc=payload.id_estado_odc,
        id_direccion_proveedor=payload.id_direccion_proveedor,
        vinculado=payload.vinculado,
    )
    db.add(obj)
    db.flush()

    # Validar que el volumen total no supere el volumen pendiente de la proforma.
    if payload.id_proforma:
        productos_proforma = {
            product_id
            for (product_id,) in (
                db.query(DetalleProforma.id_producto)
                .filter(DetalleProforma.id_proforma == payload.id_proforma)
                .distinct()
                .all()
            )
            if product_id is not None
        }

        productos_odc = {
            detalle.id_producto
            for detalle in payload.detalles
            if detalle.id_producto is not None
        }

        if productos_proforma and not productos_odc:
            raise HTTPException(
                status_code=403,
                detail="La proforma asociada tiene productos definidos; la orden de compra debe incluir id_producto en sus detalles",
            )

        productos_no_permitidos = productos_odc - productos_proforma
        if productos_no_permitidos:
            raise HTTPException(
                status_code=403,
                detail=f"La orden de compra incluye producto(s) que no existen en la proforma: {sorted(productos_no_permitidos)}",
            )

        volumen_payload = sum(_to_decimal(detalle.volumen_eq) for detalle in payload.detalles)

        volumen_proforma_total = db.query(
            func.coalesce(func.sum(DetalleProforma.volumen_eq), 0)
        ).filter(DetalleProforma.id_proforma == payload.id_proforma).scalar()

        volumen_odc_total = db.query(
            func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
        ).join(
            OrdenCompra,
            DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
        ).filter(OrdenCompra.id_proforma == payload.id_proforma).scalar()

        pendiente = _to_decimal(volumen_proforma_total) - _to_decimal(volumen_odc_total)
        if volumen_payload > pendiente:
            if pendiente <= 0:
                raise HTTPException(
                    status_code=403,
                    detail="El volumen de la proforma ya fue completado",
                )
            raise HTTPException(
                status_code=403,
                detail=f"El volumen total de la orden supera el pendiente de la proforma ({pendiente})",
            )

    for detalle in payload.detalles:
        detalle_obj = DetalleOrdenCompra(
            id_orden_compra=obj.id_orden_compra,
            **detalle.model_dump(exclude_unset=True),
        )
        db.add(detalle_obj)

    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedOrdenCompraResponse, summary='GET OrdenCompra', description='Obtener lista de órdenes de compra con paginación.', dependencies=[Depends(require_permission("orden_compra", "read"))])
def list_orden_compra(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(OrdenCompra).count()
    
    # Obtener elementos de la página actual, desde la más reciente
    items = (
        db.query(OrdenCompra)
        .order_by(desc(OrdenCompra.fecha_emision), desc(OrdenCompra.id_orden_compra))
        .offset(skip)
        .limit(page_size)
        .all()
    )
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=OrdenCompraRead, summary='GET OrdenCompra', description='Obtener una orden de compra específica por ID.', dependencies=[Depends(require_permission("orden_compra", "read"))])
def get_orden_compra(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")
    return item


@router.put("/{item_id}", response_model=OrdenCompraRead, summary='PUT OrdenCompra', description='Actualizar una orden de compra existente.', dependencies=[Depends(require_permission("orden_compra", "update"))])
def update_orden_compra(item_id: int, payload: OrdenCompraUpdate, db: Session = Depends(get_db)):
    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE OrdenCompra', description='Eliminar una orden de compra.', dependencies=[Depends(require_permission("orden_compra", "delete"))])
def delete_orden_compra(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")
    
    try:
        # Verificar si tiene detalles asociados
        from app.models.detalle_orden_compra import DetalleOrdenCompra
        detalles_count = db.query(DetalleOrdenCompra).filter(
            DetalleOrdenCompra.id_orden_compra == item_id
        ).count()
        
        if detalles_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"No se puede eliminar la orden de compra porque tiene {detalles_count} detalle(s) asociado(s)"
            )
        
        # Verificar si tiene contactos asociados
        from app.models.contacto_orden_compra import ContactoOrdenCompra
        contactos_count = db.query(ContactoOrdenCompra).filter(
            ContactoOrdenCompra.id_orden_compra == item_id
        ).count()
        
        if contactos_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"No se puede eliminar la orden de compra porque tiene {contactos_count} contacto(s) asociado(s)"
            )
        
        db.delete(item)
        db.commit()
        return {"ok": True}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al eliminar la orden de compra: {str(e)}")