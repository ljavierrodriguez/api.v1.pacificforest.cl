from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import Optional, List
from datetime import date, datetime
import os

from app.db.session import get_db
from app.models.inventario_puerto import InventarioPuerto
from app.models.guia_inventario_puerto import GuiaInventarioPuerto
from app.models.orden_servicio import OrdenServicio
from app.models.detalle_orden_servicio import DetalleOrdenServicio
from app.models.orden_compra import OrdenCompra
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.schemas.inventario_puerto import (
    InventarioPuertoCreate,
    InventarioPuertoUpdate,
    InventarioPuertoRead,
    PaginatedInventarioPuertoResponse,
    GuiaInventarioPuertoRead,
    PaginatedGuiaInventarioPuertoResponse,
    RecepcionarOrdenServicioPayload,
)

router = APIRouter(prefix="/inventario_puerto", tags=["inventario_puerto"])


@router.get(
    "/",
    response_model=PaginatedInventarioPuertoResponse,
    summary="GET InventarioPuerto",
    description="Obtener listado de inventario puerto con filtros y paginación."
)
def get_inventario_puerto(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Búsqueda por texto o ID"),
    id_orden_servicio: Optional[int] = Query(None, description="Filtrar por ID de orden de servicio"),
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

    query = db.query(InventarioPuerto)\
        .outerjoin(Producto, InventarioPuerto.id_producto == Producto.id_producto)\
        .outerjoin(Bodega, InventarioPuerto.id_bodega == Bodega.id_bodega)\
        .outerjoin(OrdenServicio, InventarioPuerto.id_orden_servicio == OrdenServicio.id_orden_servicio)\
        .outerjoin(OrdenCompra, InventarioPuerto.id_orden_compra == OrdenCompra.id_orden_compra)

    if id_orden_servicio:
        query = query.filter(InventarioPuerto.id_orden_servicio == id_orden_servicio)
    if id_orden_compra:
        query = query.filter(InventarioPuerto.id_orden_compra == id_orden_compra)
    if id_producto:
        query = query.filter(InventarioPuerto.id_producto == id_producto)
    if id_bodega:
        query = query.filter(InventarioPuerto.id_bodega == id_bodega)
    if estado:
        query = query.filter(InventarioPuerto.estado.ilike(f"%{estado}%"))

    if search and search.strip():
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                cast(InventarioPuerto.id_inventario_puerto, String).ilike(s),
                cast(InventarioPuerto.id_orden_servicio, String).ilike(s),
                cast(InventarioPuerto.id_orden_compra, String).ilike(s),
                InventarioPuerto.numero_guia.ilike(s),
                InventarioPuerto.oc.ilike(s),
                InventarioPuerto.origen.ilike(s),
                InventarioPuerto.oc_compra.ilike(s),
                InventarioPuerto.etiqueta.ilike(s),
                InventarioPuerto.texto_abierto.ilike(s),
                InventarioPuerto.observaciones.ilike(s),
                InventarioPuerto.estado.ilike(s),
                Producto.nombre_producto_esp.ilike(s),
                Bodega.nombre.ilike(s),
            )
        )

    total_items = query.count()
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    skip = (page - 1) * page_size

    items = (
        query.order_by(desc(InventarioPuerto.id_inventario_puerto))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    items_read = [InventarioPuertoRead(**item.to_dict()) for item in items]

    return PaginatedInventarioPuertoResponse(
        items=items_read,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get(
    "/guias",
    response_model=PaginatedGuiaInventarioPuertoResponse,
    summary="GET GuiaInventarioPuerto list",
    description="Obtener listado de guías de inventario puerto con sus detalles anidados."
)
def get_guias_inventario_puerto(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Búsqueda por texto"),
    id_orden_servicio: Optional[int] = Query(None, description="Filtrar por ID de orden de servicio"),
    id_orden_compra: Optional[int] = Query(None, description="Filtrar por ID de orden de compra"),
    db: Session = Depends(get_db),
):
    query = db.query(GuiaInventarioPuerto)
    if id_orden_servicio:
        query = query.filter(GuiaInventarioPuerto.id_orden_servicio == id_orden_servicio)
    if id_orden_compra:
        query = query.filter(GuiaInventarioPuerto.id_orden_compra == id_orden_compra)

    if search and search.strip():
        s = f"%{search.strip()}%"
        from app.models.producto import Producto
        from app.models.bodega import Bodega
        from app.models.cliente_proveedor import ClienteProveedor
        from sqlalchemy import cast, String

        query = (
            query.outerjoin(GuiaInventarioPuerto.detalles)
            .outerjoin(InventarioPuerto.Producto)
            .outerjoin(GuiaInventarioPuerto.Bodega)
            .outerjoin(GuiaInventarioPuerto.OrdenServicio)
            .outerjoin(GuiaInventarioPuerto.OrdenCompra)
            .filter(
                or_(
                    GuiaInventarioPuerto.numero_guia.ilike(s),
                    GuiaInventarioPuerto.oc.ilike(s),
                    GuiaInventarioPuerto.origen.ilike(s),
                    GuiaInventarioPuerto.observaciones.ilike(s),
                    InventarioPuerto.texto_abierto.ilike(s),
                    InventarioPuerto.etiqueta.ilike(s),
                    InventarioPuerto.oc_compra.ilike(s),
                    Producto.nombre_producto_esp.ilike(s),
                    Producto.nombre_producto_ing.ilike(s),
                    Bodega.nombre.ilike(s),
                    cast(GuiaInventarioPuerto.id_orden_servicio, String).ilike(s),
                    cast(GuiaInventarioPuerto.id_orden_compra, String).ilike(s),
                )
            )
            .distinct()
        )

    total_items = query.count()
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    skip = (page - 1) * page_size

    items = (
        query.order_by(desc(GuiaInventarioPuerto.id_guia_inventario_puerto))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    items_read = [GuiaInventarioPuertoRead(**item.to_dict()) for item in items]

    return PaginatedGuiaInventarioPuertoResponse(
        items=items_read,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get(
    "/resumen",
    summary="GET Resumen de Inventario Puerto",
    description="Obtener métricas agregadas de volumen, costo y desgloses por bodega y producto."
)
def get_resumen_inventario_puerto(
    id_bodega: Optional[int] = Query(None, description="Filtrar por ID de bodega"),
    db: Session = Depends(get_db),
):
    from app.models.bodega import Bodega
    from app.models.producto import Producto

    totals_query = db.query(
        func.coalesce(func.sum(InventarioPuerto.volumen), 0).label("volumen"),
        func.coalesce(func.sum(InventarioPuerto.volumen_eq), 0).label("volumen_eq"),
        func.coalesce(func.sum(InventarioPuerto.subtotal), 0).label("costo"),
        func.count(InventarioPuerto.id_inventario_puerto).label("items_count"),
        func.coalesce(func.sum(InventarioPuerto.numero_paquetes), 0).label("paquetes_count"),
        func.coalesce(func.sum(InventarioPuerto.piezas), 0).label("piezas_count")
    )
    if id_bodega:
        totals_query = totals_query.filter(InventarioPuerto.id_bodega == id_bodega)
    t = totals_query.first()

    q_bodega = (
        db.query(
            InventarioPuerto.id_bodega,
            func.coalesce(Bodega.nombre, "Sin Bodega").label("bodega_nombre"),
            func.coalesce(func.sum(InventarioPuerto.volumen), 0).label("volumen"),
            func.coalesce(func.sum(InventarioPuerto.volumen_eq), 0).label("volumen_eq"),
            func.coalesce(func.sum(InventarioPuerto.subtotal), 0).label("costo"),
            func.count(InventarioPuerto.id_inventario_puerto).label("items_count"),
            func.coalesce(func.sum(InventarioPuerto.numero_paquetes), 0).label("paquetes_count"),
        )
        .outerjoin(Bodega, InventarioPuerto.id_bodega == Bodega.id_bodega)
    )
    if id_bodega:
        q_bodega = q_bodega.filter(InventarioPuerto.id_bodega == id_bodega)
    desglose_bodegas = (
        q_bodega.group_by(InventarioPuerto.id_bodega, Bodega.nombre)
        .order_by(desc("costo"))
        .all()
    )

    q_producto = (
        db.query(
            InventarioPuerto.id_producto,
            func.coalesce(Producto.nombre_producto_esp, Producto.nombre_producto_ing, InventarioPuerto.texto_abierto, "Sin Producto").label("producto_nombre"),
            func.coalesce(func.sum(InventarioPuerto.volumen), 0).label("volumen"),
            func.coalesce(func.sum(InventarioPuerto.volumen_eq), 0).label("volumen_eq"),
            func.coalesce(func.sum(InventarioPuerto.subtotal), 0).label("costo"),
            func.count(InventarioPuerto.id_inventario_puerto).label("items_count"),
        )
        .outerjoin(Producto, InventarioPuerto.id_producto == Producto.id_producto)
    )
    if id_bodega:
        q_producto = q_producto.filter(InventarioPuerto.id_bodega == id_bodega)
    desglose_productos = (
        q_producto.group_by(InventarioPuerto.id_producto, Producto.nombre_producto_esp, Producto.nombre_producto_ing, InventarioPuerto.texto_abierto)
        .order_by(desc("costo"))
        .all()
    )

    return {
        "total_volumen": round(float(t.volumen or 0), 3),
        "total_volumen_eq": round(float(t.volumen_eq or 0), 3),
        "total_costo": round(float(t.costo or 0), 2),
        "total_items": int(t.items_count or 0),
        "total_paquetes": int(t.paquetes_count or 0),
        "total_piezas": round(float(t.piezas_count or 0), 2),
        "desglose_bodegas": [
            {
                "id_bodega": b.id_bodega,
                "nombre": b.bodega_nombre,
                "volumen": round(float(b.volumen or 0), 3),
                "volumen_eq": round(float(b.volumen_eq or 0), 3),
                "costo": round(float(b.costo or 0), 2),
                "items_count": int(b.items_count or 0),
                "paquetes_count": int(b.paquetes_count or 0),
            }
            for b in desglose_bodegas
        ],
        "desglose_productos": [
            {
                "id_producto": p.id_producto,
                "nombre": p.producto_nombre,
                "volumen": round(float(p.volumen or 0), 3),
                "volumen_eq": round(float(p.volumen_eq or 0), 3),
                "costo": round(float(p.costo or 0), 2),
                "items_count": int(p.items_count or 0),
            }
            for p in desglose_productos
        ],
    }


@router.get(
    "/{item_id}",
    response_model=InventarioPuertoRead,
    summary="GET InventarioPuerto por ID"
)
def get_inventario_puerto_by_id(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventarioPuerto).filter(InventarioPuerto.id_inventario_puerto == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Registro de inventario puerto no encontrado.")
    return InventarioPuertoRead(**item.to_dict())


@router.post(
    "/",
    response_model=InventarioPuertoRead,
    status_code=201,
    summary="POST Crear InventarioPuerto"
)
def create_inventario_puerto(
    payload: InventarioPuertoCreate,
    db: Session = Depends(get_db)
):
    db_item = InventarioPuerto(**payload.model_dump(exclude_unset=True))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return InventarioPuertoRead(**db_item.to_dict())


@router.post(
    "/recepcionar-os/{id_orden_servicio}",
    response_model=List[InventarioPuertoRead],
    status_code=201,
    summary="Recepcionar productos de una Orden de Servicio en Inventario Puerto"
)
def recepcionar_orden_servicio(
    id_orden_servicio: int,
    payload: Optional[RecepcionarOrdenServicioPayload] = None,
    db: Session = Depends(get_db)
):
    os_obj = db.query(OrdenServicio).filter(OrdenServicio.id_orden_servicio == id_orden_servicio).first()
    if not os_obj:
        raise HTTPException(status_code=404, detail=f"Orden de Servicio OS-{id_orden_servicio} no encontrada.")

    detalles = db.query(DetalleOrdenServicio).filter(DetalleOrdenServicio.id_orden_servicio == id_orden_servicio).all()
    if not detalles:
        raise HTTPException(status_code=400, detail="La Orden de Servicio no tiene productos/detalles registrados.")

    bodega_id = (payload and payload.id_bodega) or os_obj.id_bodega
    fecha_rec = (payload and payload.fecha_recepcion) or date.today()
    obs_general = (payload and payload.observaciones) or None
    top_num_guia = (payload and payload.numero_guia) or None
    top_oc = (payload and payload.oc) or None
    top_origen = (payload and payload.origen) or None
    top_url_doc = (payload and payload.url_documento) or None

    created_items = []

    if payload and payload.guias:
        detalles_by_id = {d.id_detalle_os: d for d in detalles}
        for g in payload.guias:
            g_num_guia = g.numero_guia or top_num_guia
            g_oc = g.oc or top_oc
            g_origen = g.origen or top_origen
            g_fecha = g.fecha_recepcion or fecha_rec
            g_bodega = g.id_bodega or bodega_id
            g_obs = g.observaciones or obs_general
            g_url_doc = g.url_documento or top_url_doc

            guia_header = GuiaInventarioPuerto(
                numero_guia=g_num_guia,
                oc=g_oc,
                origen=g_origen,
                id_orden_servicio=os_obj.id_orden_servicio,
                id_bodega=g_bodega,
                fecha_recepcion=g_fecha,
                url_documento=g_url_doc,
                observaciones=g_obs,
                estado="RECIBIDO",
            )
            db.add(guia_header)
            db.flush()

            g_items = g.items or []
            if g_items:
                for item_override in g_items:
                    id_det = item_override.id_detalle_os
                    d = detalles_by_id.get(id_det) if id_det else detalles[0]
                    cant = item_override.cantidad if item_override.cantidad is not None else d.cantidad
                    pzs = item_override.piezas if item_override.piezas is not None else None
                    vol = item_override.volumen if item_override.volumen is not None else d.volumen
                    vol_eq = item_override.volumen_eq if item_override.volumen_eq is not None else d.volumen_eq
                    bodega_item = item_override.id_bodega if item_override.id_bodega else g_bodega
                    obs = item_override.observaciones if item_override.observaciones else g_obs
                    item_num_guia = item_override.numero_guia if item_override.numero_guia else g_num_guia
                    item_oc = item_override.oc or g_oc
                    item_origen = item_override.origen or g_origen
                    item_oc_compra = item_override.oc_compra or None
                    item_etiqueta = item_override.etiqueta or None
                    item_paquetes = item_override.numero_paquetes if item_override.numero_paquetes is not None else None
                    item_url_doc = item_override.url_documento or g_url_doc

                    esp = item_override.espesor if item_override.espesor is not None else d.espesor
                    anc = item_override.ancho if item_override.ancho is not None else d.ancho
                    lar = item_override.largo if item_override.largo is not None else d.largo
                    calc_subtotal = round(float(cant or vol_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((cant or vol_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal

                    inv = InventarioPuerto(
                        id_guia_inventario_puerto=guia_header.id_guia_inventario_puerto,
                        id_orden_servicio=os_obj.id_orden_servicio,
                        id_detalle_os=d.id_detalle_os,
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
                        subtotal=calc_subtotal,
                        volumen=vol,
                        volumen_eq=vol_eq,
                        precio_eq=d.precio_eq,
                        piezas=pzs,
                        fecha_recepcion=g_fecha,
                        numero_guia=item_num_guia,
                        oc=item_oc,
                        origen=item_origen,
                        oc_compra=item_oc_compra,
                        etiqueta=item_etiqueta,
                        numero_paquetes=item_paquetes,
                        url_documento=item_url_doc,
                        observaciones=obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
            else:
                for d in detalles:
                    calc_subtotal = round(float(d.cantidad or d.volumen_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((d.cantidad or d.volumen_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal
                    inv = InventarioPuerto(
                        id_guia_inventario_puerto=guia_header.id_guia_inventario_puerto,
                        id_orden_servicio=os_obj.id_orden_servicio,
                        id_detalle_os=d.id_detalle_os,
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
                        subtotal=calc_subtotal,
                        volumen=d.volumen,
                        volumen_eq=d.volumen_eq,
                        precio_eq=d.precio_eq,
                        fecha_recepcion=g_fecha,
                        numero_guia=g_num_guia,
                        oc=g_oc,
                        origen=g_origen,
                        url_documento=g_url_doc,
                        observaciones=g_obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
    else:
        guia_header = GuiaInventarioPuerto(
            numero_guia=top_num_guia,
            oc=top_oc,
            origen=top_origen,
            id_orden_servicio=os_obj.id_orden_servicio,
            id_bodega=bodega_id,
            fecha_recepcion=fecha_rec,
            url_documento=top_url_doc,
            observaciones=obs_general,
            estado="RECIBIDO",
        )
        db.add(guia_header)
        db.flush()

        items_map = {}
        if payload and payload.items:
            for item in payload.items:
                if item.id_detalle_os:
                    items_map[item.id_detalle_os] = item

        for d in detalles:
            item_override = items_map.get(d.id_detalle_os)
            cant = item_override.cantidad if (item_override and item_override.cantidad is not None) else d.cantidad
            pzs = item_override.piezas if (item_override and item_override.piezas is not None) else None
            vol = item_override.volumen if (item_override and item_override.volumen is not None) else d.volumen
            vol_eq = item_override.volumen_eq if (item_override and item_override.volumen_eq is not None) else d.volumen_eq
            bodega_item = item_override.id_bodega if (item_override and item_override.id_bodega) else bodega_id
            obs = item_override.observaciones if (item_override and item_override.observaciones) else obs_general
            num_guia = (item_override and item_override.numero_guia) or top_num_guia
            oc_val = (item_override and item_override.oc) or top_oc
            origen_val = (item_override and item_override.origen) or top_origen
            oc_c_val = item_override and item_override.oc_compra
            etq = item_override and item_override.etiqueta
            pqs = item_override and item_override.numero_paquetes
            doc = (item_override and item_override.url_documento) or top_url_doc

            esp = item_override.espesor if (item_override and item_override.espesor is not None) else d.espesor
            anc = item_override.ancho if (item_override and item_override.ancho is not None) else d.ancho
            lar = item_override.largo if (item_override and item_override.largo is not None) else d.largo
            txt = item_override.texto_abierto if (item_override and item_override.texto_abierto is not None) else d.texto_abierto

            inv = InventarioPuerto(
                id_guia_inventario_puerto=guia_header.id_guia_inventario_puerto,
                id_orden_servicio=os_obj.id_orden_servicio,
                id_detalle_os=d.id_detalle_os,
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
                subtotal=round(float(cant or vol_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((cant or vol_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal,
                volumen=vol,
                volumen_eq=vol_eq,
                precio_eq=d.precio_eq,
                piezas=pzs,
                fecha_recepcion=fecha_rec,
                numero_guia=num_guia,
                oc=oc_val,
                origen=origen_val,
                oc_compra=oc_c_val,
                etiqueta=etq,
                numero_paquetes=pqs,
                url_documento=doc,
                observaciones=obs,
                estado="RECIBIDO",
            )
            db.add(inv)
            created_items.append(inv)

    db.commit()

    for item in created_items:
        db.refresh(item)

    return [InventarioPuertoRead(**item.to_dict()) for item in created_items]


@router.post(
    "/recepcionar-oc/{id_orden_compra}",
    response_model=List[InventarioPuertoRead],
    status_code=201,
    summary="Recepcionar productos de una Orden de Compra en Inventario Puerto"
)
def recepcionar_orden_compra_puerto(
    id_orden_compra: int,
    payload: Optional[RecepcionarOrdenServicioPayload] = None,
    db: Session = Depends(get_db)
):
    oc_obj = db.query(OrdenCompra).filter(OrdenCompra.id_orden_compra == id_orden_compra).first()
    if not oc_obj:
        raise HTTPException(status_code=404, detail=f"Orden de Compra OC-{id_orden_compra} no encontrada.")

    detalles = db.query(DetalleOrdenCompra).filter(DetalleOrdenCompra.id_orden_compra == id_orden_compra).all()
    if not detalles:
        raise HTTPException(status_code=400, detail="La Orden de Compra no tiene productos/detalles registrados.")

    bodega_id = (payload and payload.id_bodega) or oc_obj.id_bodega
    fecha_rec = (payload and payload.fecha_recepcion) or date.today()
    obs_general = (payload and payload.observaciones) or None
    top_num_guia = (payload and payload.numero_guia) or None
    top_oc = (payload and payload.oc) or str(oc_obj.id_orden_compra)
    top_origen = (payload and payload.origen) or None
    top_url_doc = (payload and payload.url_documento) or None

    created_items = []

    if payload and payload.guias:
        detalles_by_id = {d.id_detalle_odc: d for d in detalles}
        for g in payload.guias:
            g_num_guia = g.numero_guia or top_num_guia
            g_oc = g.oc or top_oc
            g_origen = g.origen or top_origen
            g_fecha = g.fecha_recepcion or fecha_rec
            g_bodega = g.id_bodega or bodega_id
            g_obs = g.observaciones or obs_general
            g_url_doc = g.url_documento or top_url_doc

            guia_header = GuiaInventarioPuerto(
                numero_guia=g_num_guia,
                oc=g_oc,
                origen=g_origen,
                id_orden_compra=oc_obj.id_orden_compra,
                id_bodega=g_bodega,
                fecha_recepcion=g_fecha,
                url_documento=g_url_doc,
                observaciones=g_obs,
                estado="RECIBIDO",
            )
            db.add(guia_header)
            db.flush()

            g_items = g.items or []
            if g_items:
                for item_override in g_items:
                    id_det = item_override.id_detalle_odc or item_override.id_detalle_os
                    d = detalles_by_id.get(id_det) if id_det else detalles[0]
                    cant = item_override.cantidad if item_override.cantidad is not None else d.cantidad
                    pzs = item_override.piezas if item_override.piezas is not None else None
                    vol = item_override.volumen if item_override.volumen is not None else d.volumen
                    vol_eq = item_override.volumen_eq if item_override.volumen_eq is not None else d.volumen_eq
                    bodega_item = item_override.id_bodega if item_override.id_bodega else g_bodega
                    obs = item_override.observaciones if item_override.observaciones else g_obs
                    item_num_guia = item_override.numero_guia if item_override.numero_guia else g_num_guia
                    item_oc = item_override.oc or g_oc
                    item_origen = item_override.origen or g_origen
                    item_oc_compra = item_override.oc_compra or None
                    item_etiqueta = item_override.etiqueta or None
                    item_paquetes = item_override.numero_paquetes if item_override.numero_paquetes is not None else None
                    item_url_doc = item_override.url_documento or g_url_doc

                    esp = item_override.espesor if item_override.espesor is not None else d.espesor
                    anc = item_override.ancho if item_override.ancho is not None else d.ancho
                    lar = item_override.largo if item_override.largo is not None else d.largo
                    txt = item_override.texto_abierto if item_override.texto_abierto is not None else d.texto_abierto
                    calc_subtotal = round(float(cant or vol_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((cant or vol_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal

                    inv = InventarioPuerto(
                        id_guia_inventario_puerto=guia_header.id_guia_inventario_puerto,
                        id_orden_compra=oc_obj.id_orden_compra,
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
                        subtotal=calc_subtotal,
                        volumen=vol,
                        volumen_eq=vol_eq,
                        precio_eq=d.precio_eq,
                        piezas=pzs,
                        fecha_recepcion=g_fecha,
                        numero_guia=item_num_guia,
                        oc=item_oc,
                        origen=item_origen,
                        oc_compra=item_oc_compra,
                        etiqueta=item_etiqueta,
                        numero_paquetes=item_paquetes,
                        url_documento=item_url_doc,
                        observaciones=obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
            else:
                for d in detalles:
                    calc_subtotal = round(float(d.cantidad or d.volumen_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((d.cantidad or d.volumen_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal
                    inv = InventarioPuerto(
                        id_guia_inventario_puerto=guia_header.id_guia_inventario_puerto,
                        id_orden_compra=oc_obj.id_orden_compra,
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
                        subtotal=calc_subtotal,
                        volumen=d.volumen,
                        volumen_eq=d.volumen_eq,
                        precio_eq=d.precio_eq,
                        fecha_recepcion=g_fecha,
                        numero_guia=g_num_guia,
                        oc=g_oc,
                        origen=g_origen,
                        url_documento=g_url_doc,
                        observaciones=g_obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
    else:
        guia_header = GuiaInventarioPuerto(
            numero_guia=top_num_guia,
            oc=top_oc,
            origen=top_origen,
            id_orden_compra=oc_obj.id_orden_compra,
            id_bodega=bodega_id,
            fecha_recepcion=fecha_rec,
            url_documento=top_url_doc,
            observaciones=obs_general,
            estado="RECIBIDO",
        )
        db.add(guia_header)
        db.flush()

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
            num_guia = (item_override and item_override.numero_guia) or top_num_guia
            oc_val = (item_override and item_override.oc) or top_oc
            origen_val = (item_override and item_override.origen) or top_origen
            oc_c_val = item_override and item_override.oc_compra
            etq = item_override and item_override.etiqueta
            pqs = item_override and item_override.numero_paquetes
            doc = (item_override and item_override.url_documento) or top_url_doc

            esp = item_override.espesor if (item_override and item_override.espesor is not None) else d.espesor
            anc = item_override.ancho if (item_override and item_override.ancho is not None) else d.ancho
            lar = item_override.largo if (item_override and item_override.largo is not None) else d.largo
            txt = item_override.texto_abierto if (item_override and item_override.texto_abierto is not None) else d.texto_abierto
            calc_subtotal = round(float(cant or vol_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((cant or vol_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal

            inv = InventarioPuerto(
                id_guia_inventario_puerto=guia_header.id_guia_inventario_puerto,
                id_orden_compra=oc_obj.id_orden_compra,
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
                subtotal=calc_subtotal,
                volumen=vol,
                volumen_eq=vol_eq,
                precio_eq=d.precio_eq,
                piezas=pzs,
                fecha_recepcion=fecha_rec,
                numero_guia=num_guia,
                oc=oc_val,
                origen=origen_val,
                oc_compra=oc_c_val,
                etiqueta=etq,
                numero_paquetes=pqs,
                url_documento=doc,
                observaciones=obs,
                estado="RECIBIDO",
            )
            db.add(inv)
            created_items.append(inv)

    db.commit()

    for item in created_items:
        db.refresh(item)

    return [InventarioPuertoRead(**item.to_dict()) for item in created_items]


@router.post(
    "/guia/documento",
    summary="Subir documento anexo para una Guía de Despacho en Puerto",
    description="Sube un archivo (PDF, imagen, etc.) y lo asocia a todas las entradas con ese numero_guia en puerto."
)
def upload_documento_guia_puerto(
    numero_guia: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not numero_guia or not numero_guia.strip():
        raise HTTPException(status_code=400, detail="Debe especificar un número de guía.")
    
    clean_guia = numero_guia.strip()
    headers = db.query(GuiaInventarioPuerto).filter(GuiaInventarioPuerto.numero_guia == clean_guia).all()
    items = db.query(InventarioPuerto).filter(InventarioPuerto.numero_guia == clean_guia).all()

    static_path = os.path.join(os.getcwd(), "app", "static", "documentos_guias_puerto")
    os.makedirs(static_path, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_guia = clean_guia.replace("/", "_").replace("\\", "_")
    unique_filename = f"guia_puerto_{safe_guia}_{timestamp}{file_extension}"
    file_path = os.path.join(static_path, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
        
    url_documento = f"/static/documentos_guias_puerto/{unique_filename}"
    
    for h in headers:
        h.url_documento = url_documento
    for item in items:
        item.url_documento = url_documento
    db.commit()
    
    return {"ok": True, "numero_guia": clean_guia, "url_documento": url_documento}


@router.delete(
    "/guia/{guia_id}",
    summary="DELETE Eliminar Guía de Despacho en Puerto e Ítems",
    description="Elimina la guía de despacho de puerto por ID y todos sus ítems asociados."
)
def delete_guia_inventario_puerto(guia_id: int, db: Session = Depends(get_db)):
    guia = db.query(GuiaInventarioPuerto).filter(GuiaInventarioPuerto.id_guia_inventario_puerto == guia_id).first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía de inventario puerto no encontrada.")

    db.delete(guia)
    db.commit()
    return {"ok": True, "message": f"Guía #{guia_id} y sus productos eliminados exitosamente."}


@router.put(
    "/{item_id}",
    response_model=InventarioPuertoRead,
    summary="PUT Actualizar InventarioPuerto"
)
def update_inventario_puerto(
    item_id: int,
    payload: InventarioPuertoUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(InventarioPuerto).filter(InventarioPuerto.id_inventario_puerto == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Registro de inventario puerto no encontrado.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return InventarioPuertoRead(**item.to_dict())


@router.delete(
    "/{item_id}",
    summary="DELETE Eliminar InventarioPuerto"
)
def delete_inventario_puerto(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventarioPuerto).filter(InventarioPuerto.id_inventario_puerto == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Registro de inventario puerto no encontrado.")

    db.delete(item)
    db.commit()
    return {"ok": True, "message": f"Registro {item_id} eliminado exitosamente."}
