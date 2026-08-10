from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional, List
from datetime import date

from app.db.session import get_db
from app.models.inventario_transitorio import InventarioTransitorio
from app.models.orden_compra import OrdenCompra
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.schemas.inventario_transitorio import (
    InventarioTransitorioCreate,
    InventarioTransitorioUpdate,
    InventarioTransitorioRead,
    PaginatedInventarioTransitorioResponse,
    RecepcionarOrdenCompraPayload,
)

router = APIRouter(prefix="/inventario_transitorio", tags=["inventario_transitorio"])


@router.get(
    "/",
    response_model=PaginatedInventarioTransitorioResponse,
    summary="GET InventarioTransitorio",
    description="Obtener listado de inventario transitorio con filtros y paginación."
)
def get_inventario_transitorio(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Búsqueda por texto o ID"),
    id_orden_compra: Optional[int] = Query(None, description="Filtrar por ID de orden de compra"),
    id_producto: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    id_bodega: Optional[int] = Query(None, description="Filtrar por ID de bodega"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
):
    from app.models.producto import Producto
    from app.models.bodega import Bodega
    from app.models.cliente_proveedor import ClienteProveedor
    from sqlalchemy import cast, String

    query = db.query(InventarioTransitorio)\
        .outerjoin(Producto, InventarioTransitorio.id_producto == Producto.id_producto)\
        .outerjoin(Bodega, InventarioTransitorio.id_bodega == Bodega.id_bodega)\
        .outerjoin(OrdenCompra, InventarioTransitorio.id_orden_compra == OrdenCompra.id_orden_compra)\
        .outerjoin(ClienteProveedor, OrdenCompra.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor)

    if id_orden_compra:
        query = query.filter(InventarioTransitorio.id_orden_compra == id_orden_compra)
    if id_producto:
        query = query.filter(InventarioTransitorio.id_producto == id_producto)
    if id_bodega:
        query = query.filter(InventarioTransitorio.id_bodega == id_bodega)
    if estado:
        query = query.filter(InventarioTransitorio.estado.ilike(f"%{estado}%"))

    if search and search.strip():
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                cast(InventarioTransitorio.id_inventario_transitorio, String).ilike(s),
                cast(InventarioTransitorio.id_orden_compra, String).ilike(s),
                InventarioTransitorio.numero_guia.ilike(s),
                InventarioTransitorio.texto_abierto.ilike(s),
                InventarioTransitorio.observaciones.ilike(s),
                InventarioTransitorio.estado.ilike(s),
                Producto.nombre_producto_esp.ilike(s),
                Bodega.nombre.ilike(s),
                ClienteProveedor.razon_social.ilike(s),
                ClienteProveedor.nombre_fantasia.ilike(s),
            )
        )

    total_items = query.count()
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    skip = (page - 1) * page_size

    items = (
        query.order_by(desc(InventarioTransitorio.id_inventario_transitorio))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    items_read = [InventarioTransitorioRead(**item.to_dict()) for item in items]

    return PaginatedInventarioTransitorioResponse(
        items=items_read,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get(
    "/{item_id}",
    response_model=InventarioTransitorioRead,
    summary="GET InventarioTransitorio por ID"
)
def get_inventario_transitorio_by_id(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventarioTransitorio).filter(InventarioTransitorio.id_inventario_transitorio == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Registro de inventario transitorio no encontrado.")
    return InventarioTransitorioRead(**item.to_dict())


@router.post(
    "/",
    response_model=InventarioTransitorioRead,
    status_code=201,
    summary="POST Crear InventarioTransitorio"
)
def create_inventario_transitorio(
    payload: InventarioTransitorioCreate,
    db: Session = Depends(get_db)
):
    db_item = InventarioTransitorio(**payload.model_dump(exclude_unset=True))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return InventarioTransitorioRead(**db_item.to_dict())


@router.post(
    "/recepcionar-oc/{id_orden_compra}",
    response_model=List[InventarioTransitorioRead],
    status_code=201,
    summary="Recepcionar productos de una Orden de Compra en Inventario Transitorio"
)
def recepcionar_orden_compra(
    id_orden_compra: int,
    payload: Optional[RecepcionarOrdenCompraPayload] = None,
    db: Session = Depends(get_db)
):
    oc = db.query(OrdenCompra).filter(OrdenCompra.id_orden_compra == id_orden_compra).first()
    if not oc:
        raise HTTPException(status_code=404, detail=f"Orden de Compra OC-{id_orden_compra} no encontrada.")

    detalles = db.query(DetalleOrdenCompra).filter(DetalleOrdenCompra.id_orden_compra == id_orden_compra).all()
    if not detalles:
        raise HTTPException(status_code=400, detail="La Orden de Compra no tiene productos registrados.")

    bodega_id = (payload and payload.id_bodega) or oc.id_bodega
    fecha_rec = (payload and payload.fecha_recepcion) or date.today()
    obs_general = (payload and payload.observaciones) or None
    top_numero_guia = (payload and payload.numero_guia) or None

    created_items = []

    # Caso 1: Se envían múltiples guías de despacho explícitas
    if payload and payload.guias:
        detalles_by_id = {d.id_detalle_odc: d for d in detalles}
        for g in payload.guias:
            g_num_guia = g.numero_guia or top_numero_guia
            g_fecha = g.fecha_recepcion or fecha_rec
            g_bodega = g.id_bodega or bodega_id
            g_obs = g.observaciones or obs_general

            g_items = g.items or []
            # Si la guía incluye ítems específicos
            if g_items:
                for item_override in g_items:
                    id_det = item_override.id_detalle_odc
                    d = detalles_by_id.get(id_det) if id_det else None
                    if not d:
                        continue
                    cant = item_override.cantidad if item_override.cantidad is not None else d.cantidad
                    pzs = item_override.piezas if item_override.piezas is not None else None
                    vol = item_override.volumen if item_override.volumen is not None else d.volumen
                    vol_eq = item_override.volumen_eq if item_override.volumen_eq is not None else d.volumen_eq
                    bodega_item = item_override.id_bodega if item_override.id_bodega else g_bodega
                    obs = item_override.observaciones if item_override.observaciones else g_obs
                    item_num_guia = item_override.numero_guia if item_override.numero_guia else g_num_guia

                    esp = item_override.espesor if item_override.espesor is not None else d.espesor
                    anc = item_override.ancho if item_override.ancho is not None else d.ancho
                    lar = item_override.largo if item_override.largo is not None else d.largo
                    txt = item_override.texto_abierto if item_override.texto_abierto is not None else d.texto_abierto

                    inv = InventarioTransitorio(
                        id_orden_compra=oc.id_orden_compra,
                        id_detalle_odc=d.id_detalle_odc,
                        id_producto=d.id_producto,
                        id_bodega=bodega_item,
                        id_unidad_venta=d.id_unidad_venta,
                        texto_abierto=txt,
                        espesor=esp,
                        id_unidad_medida_espesor=d.id_unidad_medida_espesor,
                        ancho=anc,
                        id_unidad_medida_ancho=d.id_unidad_medida_ancho,
                        largo=lar,
                        id_unidad_medida_largo=d.id_unidad_medida_largo,
                        cantidad=cant,
                        precio_unitario=d.precio_unitario,
                        subtotal=d.subtotal,
                        volumen=vol,
                        volumen_eq=vol_eq,
                        precio_eq=d.precio_eq,
                        piezas=pzs,
                        fecha_recepcion=g_fecha,
                        numero_guia=item_num_guia,
                        observaciones=obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
            else:
                # Si no especificó ítems en esta guía, agregar todos los detalles con los datos de la guía
                for d in detalles:
                    inv = InventarioTransitorio(
                        id_orden_compra=oc.id_orden_compra,
                        id_detalle_odc=d.id_detalle_odc,
                        id_producto=d.id_producto,
                        id_bodega=g_bodega,
                        id_unidad_venta=d.id_unidad_venta,
                        texto_abierto=d.texto_abierto,
                        espesor=d.espesor,
                        id_unidad_medida_espesor=d.id_unidad_medida_espesor,
                        ancho=d.ancho,
                        id_unidad_medida_ancho=d.id_unidad_medida_ancho,
                        largo=d.largo,
                        id_unidad_medida_largo=d.id_unidad_medida_largo,
                        cantidad=d.cantidad,
                        precio_unitario=d.precio_unitario,
                        subtotal=d.subtotal,
                        volumen=d.volumen,
                        volumen_eq=d.volumen_eq,
                        precio_eq=d.precio_eq,
                        fecha_recepcion=g_fecha,
                        numero_guia=g_num_guia,
                        observaciones=g_obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
    else:
        # Caso 2: Recepción simple / legacy (un solo bloque de items)
        items_map = {}
        if payload and payload.items:
            for item in payload.items:
                if item.id_detalle_odc:
                    items_map[item.id_detalle_odc] = item

        for d in detalles:
            item_override = items_map.get(d.id_detalle_odc)
            cant = item_override.cantidad if (item_override and item_override.cantidad is not None) else d.cantidad
            pzs = item_override.piezas if (item_override and item_override.piezas is not None) else None
            vol = item_override.volumen if (item_override and item_override.volumen is not None) else d.volumen
            vol_eq = item_override.volumen_eq if (item_override and item_override.volumen_eq is not None) else d.volumen_eq
            bodega_item = item_override.id_bodega if (item_override and item_override.id_bodega) else bodega_id
            obs = item_override.observaciones if (item_override and item_override.observaciones) else obs_general
            num_guia = item_override.numero_guia if (item_override and item_override.numero_guia) else top_numero_guia

            esp = item_override.espesor if (item_override and item_override.espesor is not None) else d.espesor
            anc = item_override.ancho if (item_override and item_override.ancho is not None) else d.ancho
            lar = item_override.largo if (item_override and item_override.largo is not None) else d.largo
            txt = item_override.texto_abierto if (item_override and item_override.texto_abierto is not None) else d.texto_abierto

            inv = InventarioTransitorio(
                id_orden_compra=oc.id_orden_compra,
                id_detalle_odc=d.id_detalle_odc,
                id_producto=d.id_producto,
                id_bodega=bodega_item,
                id_unidad_venta=d.id_unidad_venta,
                texto_abierto=txt,
                espesor=esp,
                id_unidad_medida_espesor=d.id_unidad_medida_espesor,
                ancho=anc,
                id_unidad_medida_ancho=d.id_unidad_medida_ancho,
                largo=lar,
                id_unidad_medida_largo=d.id_unidad_medida_largo,
                cantidad=cant,
                precio_unitario=d.precio_unitario,
                subtotal=d.subtotal,
                volumen=vol,
                volumen_eq=vol_eq,
                precio_eq=d.precio_eq,
                piezas=pzs,
                fecha_recepcion=fecha_rec,
                numero_guia=num_guia,
                observaciones=obs,
                estado="RECIBIDO",
            )
            db.add(inv)
            created_items.append(inv)

    db.commit()

    for item in created_items:
        db.refresh(item)

    return [InventarioTransitorioRead(**item.to_dict()) for item in created_items]


@router.put(
    "/{item_id}",
    response_model=InventarioTransitorioRead,
    summary="PUT Actualizar InventarioTransitorio"
)
def update_inventario_transitorio(
    item_id: int,
    payload: InventarioTransitorioUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(InventarioTransitorio).filter(InventarioTransitorio.id_inventario_transitorio == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Registro de inventario transitorio no encontrado.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return InventarioTransitorioRead(**item.to_dict())


@router.delete(
    "/{item_id}",
    summary="DELETE Eliminar InventarioTransitorio"
)
def delete_inventario_transitorio(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventarioTransitorio).filter(InventarioTransitorio.id_inventario_transitorio == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Registro de inventario transitorio no encontrado.")

    db.delete(item)
    db.commit()
    return {"ok": True, "message": f"Registro {item_id} eliminado exitosamente."}
