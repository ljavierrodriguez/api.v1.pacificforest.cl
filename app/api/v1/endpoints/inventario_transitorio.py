from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
from typing import Optional, List
from datetime import date, datetime
import os

from app.db.session import get_db
from app.models.inventario_transitorio import InventarioTransitorio
from app.models.guia_inventario_transitorio import GuiaInventarioTransitorio
from app.models.orden_compra import OrdenCompra
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.schemas.inventario_transitorio import (
    InventarioTransitorioCreate,
    InventarioTransitorioUpdate,
    InventarioTransitorioRead,
    PaginatedInventarioTransitorioResponse,
    GuiaInventarioTransitorioRead,
    PaginatedGuiaInventarioTransitorioResponse,
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
                InventarioTransitorio.numero_proforma.ilike(s),
                InventarioTransitorio.etiqueta.ilike(s),
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
    "/guias",
    response_model=PaginatedGuiaInventarioTransitorioResponse,
    summary="GET GuiaInventarioTransitorio list",
    description="Obtener listado de guías de inventario transitorio con sus detalles anidados."
)
def get_guias_inventario_transitorio(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Búsqueda por texto"),
    id_orden_compra: Optional[int] = Query(None, description="Filtrar por ID de orden de compra"),
    db: Session = Depends(get_db),
):
    query = db.query(GuiaInventarioTransitorio)
    if id_orden_compra:
        query = query.filter(GuiaInventarioTransitorio.id_orden_compra == id_orden_compra)
    if search and search.strip():
        s = f"%{search.strip()}%"
        from app.models.producto import Producto
        from app.models.bodega import Bodega
        from app.models.cliente_proveedor import ClienteProveedor
        from sqlalchemy import cast, String

        query = (
            query.outerjoin(GuiaInventarioTransitorio.detalles)
            .outerjoin(InventarioTransitorio.Producto)
            .outerjoin(GuiaInventarioTransitorio.Bodega)
            .outerjoin(GuiaInventarioTransitorio.OrdenCompra)
            .outerjoin(OrdenCompra.ClienteProveedor)
            .filter(
                or_(
                    GuiaInventarioTransitorio.numero_guia.ilike(s),
                    GuiaInventarioTransitorio.numero_proforma.ilike(s),
                    GuiaInventarioTransitorio.observaciones.ilike(s),
                    InventarioTransitorio.texto_abierto.ilike(s),
                    InventarioTransitorio.etiqueta.ilike(s),
                    Producto.nombre_producto_esp.ilike(s),
                    Producto.nombre_producto_ing.ilike(s),
                    Bodega.nombre.ilike(s),
                    ClienteProveedor.razon_social.ilike(s),
                    cast(GuiaInventarioTransitorio.id_orden_compra, String).ilike(s),
                )
            )
            .distinct()
        )

    total_items = query.count()
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    skip = (page - 1) * page_size

    items = (
        query.order_by(desc(GuiaInventarioTransitorio.id_guia_inventario_transitorio))
        .offset(skip)
        .limit(page_size)
        .all()
    )

    items_read = [GuiaInventarioTransitorioRead(**item.to_dict()) for item in items]

    return PaginatedGuiaInventarioTransitorioResponse(
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
    summary="GET Resumen de Inventario Transitorio",
    description="Obtener métricas agregadas de volumen, costo y desgloses por bodega y producto."
)
def get_resumen_inventario_transitorio(
    id_bodega: Optional[int] = Query(None, description="Filtrar por ID de bodega"),
    db: Session = Depends(get_db),
):
    from app.models.orden_servicio import OrdenServicio
    from app.models.guia_costo_servicio import GuiaCostoServicio

    q = db.query(InventarioTransitorio)
    if id_bodega:
        q = q.filter(InventarioTransitorio.id_bodega == id_bodega)
    items = q.all()

    item_dicts = [t.to_dict() for t in items]
    total_volumen = round(sum(d.get("volumen") or 0 for d in item_dicts), 3)
    total_volumen_eq = round(sum(d.get("volumen_eq") or 0 for d in item_dicts), 3)
    total_costo_producto = round(sum(d.get("subtotal") or 0 for d in item_dicts), 2)
    total_items = len(item_dicts)
    total_paquetes = sum(d.get("numero_paquetes") or 1 for d in item_dicts)
    total_piezas = round(sum(d.get("piezas") or 0 for d in item_dicts), 2)

    # Calculate linked fletes
    os_ids = set()
    for t in items:
        if t.id_orden_compra:
            linked_os = db.query(OrdenServicio).filter(OrdenServicio.id_orden_compra == t.id_orden_compra).all()
            for los in linked_os:
                os_ids.add(los.id_orden_servicio)

    guias_numeros = {t.numero_guia for t in items if t.numero_guia}
    for gnum in guias_numeros:
        gcs = db.query(GuiaCostoServicio).filter(GuiaCostoServicio.numero_guia == gnum).first()
        if gcs:
            for los in gcs.ordenes_servicio:
                os_ids.add(los.id_orden_servicio)

    total_flete = 0
    for os_id in os_ids:
        os = db.query(OrdenServicio).filter(OrdenServicio.id_orden_servicio == os_id).first()
        if os and os.flete:
            total_flete += float(os.flete)
    total_flete = round(total_flete, 2)
    total_costo = round(total_costo_producto + total_flete, 2)

    # Breakdown by bodega
    bodega_groups = {}
    for d in item_dicts:
        bid = d.get("id_bodega")
        bname = d.get("bodega_nombre") or "Sin Bodega"
        if bid not in bodega_groups:
            bodega_groups[bid] = {
                "id_bodega": bid,
                "nombre": bname,
                "volumen": 0,
                "volumen_eq": 0,
                "costo_producto": 0,
                "costo_flete": 0,
                "costo": 0,
                "items_count": 0,
                "paquetes_count": 0
            }
        bodega_groups[bid]["volumen"] += d.get("volumen") or 0
        bodega_groups[bid]["volumen_eq"] += d.get("volumen_eq") or 0
        bodega_groups[bid]["costo_producto"] += d.get("subtotal") or 0
        bodega_groups[bid]["items_count"] += 1
        bodega_groups[bid]["paquetes_count"] += d.get("numero_paquetes") or 1

    desglose_bodegas = []
    for bid, bg in bodega_groups.items():
        bg["volumen"] = round(bg["volumen"], 3)
        bg["volumen_eq"] = round(bg["volumen_eq"], 3)
        bg["costo_producto"] = round(bg["costo_producto"], 2)
        b_flete = round((bg["volumen"] / (total_volumen or 1)) * total_flete, 2) if total_volumen > 0 else 0
        bg["costo_flete"] = b_flete
        bg["costo"] = round(bg["costo_producto"] + b_flete, 2)
        desglose_bodegas.append(bg)

    desglose_bodegas.sort(key=lambda x: x["costo"], reverse=True)

    # Breakdown by producto
    prod_groups = {}
    for d in item_dicts:
        pid = d.get("id_producto")
        pname = d.get("producto_nombre") or d.get("texto_abierto") or "Sin Producto"
        if pid not in prod_groups:
            prod_groups[pid] = {
                "id_producto": pid,
                "nombre": pname,
                "volumen": 0,
                "volumen_eq": 0,
                "costo_producto": 0,
                "costo_flete": 0,
                "costo": 0,
                "items_count": 0
            }
        prod_groups[pid]["volumen"] += d.get("volumen") or 0
        prod_groups[pid]["volumen_eq"] += d.get("volumen_eq") or 0
        prod_groups[pid]["costo_producto"] += d.get("subtotal") or 0
        prod_groups[pid]["items_count"] += 1

    desglose_productos = []
    for pid, pg in prod_groups.items():
        pg["volumen"] = round(pg["volumen"], 3)
        pg["volumen_eq"] = round(pg["volumen_eq"], 3)
        pg["costo_producto"] = round(pg["costo_producto"], 2)
        p_flete = round((pg["volumen"] / (total_volumen or 1)) * total_flete, 2) if total_volumen > 0 else 0
        pg["costo_flete"] = p_flete
        pg["costo"] = round(pg["costo_producto"] + p_flete, 2)
        desglose_productos.append(pg)

    desglose_productos.sort(key=lambda x: x["costo"], reverse=True)

    return {
        "total_volumen": total_volumen,
        "total_volumen_eq": total_volumen_eq,
        "total_costo_producto": total_costo_producto,
        "total_flete": total_flete,
        "total_costo": total_costo,
        "total_items": total_items,
        "total_paquetes": total_paquetes,
        "total_piezas": total_piezas,
        "desglose_bodegas": desglose_bodegas,
        "desglose_productos": desglose_productos,
    }


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
    top_numero_pf = (payload and payload.numero_proforma) or (f"PF-{oc.id_proforma}" if oc.id_proforma else None)
    top_url_doc = (payload and payload.url_documento) or None

    created_items = []

    # Caso 1: Se envían múltiples guías de despacho explícitas
    if payload and payload.guias:
        detalles_by_id = {d.id_detalle_odc: d for d in detalles}
        for g in payload.guias:
            g_num_guia = g.numero_guia or top_numero_guia
            g_fecha = g.fecha_recepcion or fecha_rec
            g_bodega = g.id_bodega or bodega_id
            g_obs = g.observaciones or obs_general
            g_num_pf = g.numero_proforma or top_numero_pf
            g_url_doc = g.url_documento or top_url_doc

            # Crear registro de cabecera normalizado
            guia_header = GuiaInventarioTransitorio(
                numero_guia=g_num_guia,
                numero_proforma=g_num_pf,
                id_orden_compra=oc.id_orden_compra,
                id_bodega=g_bodega,
                fecha_recepcion=g_fecha,
                url_documento=g_url_doc,
                observaciones=g_obs,
                estado="RECIBIDO",
            )
            db.add(guia_header)
            db.flush()

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
                    item_num_pf = item_override.numero_proforma or g_num_pf
                    item_etiqueta = item_override.etiqueta or None
                    item_paquetes = item_override.numero_paquetes if item_override.numero_paquetes is not None else None
                    item_url_doc = item_override.url_documento or g_url_doc

                    esp = item_override.espesor if item_override.espesor is not None else d.espesor
                    anc = item_override.ancho if item_override.ancho is not None else d.ancho
                    lar = item_override.largo if item_override.largo is not None else d.largo
                    txt = item_override.texto_abierto if item_override.texto_abierto is not None else d.texto_abierto
                    calc_subtotal = round(float(cant or vol_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((cant or vol_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal

                    inv = InventarioTransitorio(
                        id_guia_inventario_transitorio=guia_header.id_guia_inventario_transitorio,
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
                        subtotal=calc_subtotal,
                        volumen=vol,
                        volumen_eq=vol_eq,
                        precio_eq=d.precio_eq,
                        piezas=pzs,
                        fecha_recepcion=g_fecha,
                        numero_guia=item_num_guia,
                        numero_proforma=item_num_pf,
                        etiqueta=item_etiqueta,
                        numero_paquetes=item_paquetes,
                        url_documento=item_url_doc,
                        observaciones=obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
            else:
                # Si no especificó ítems en esta guía, agregar todos los detalles con los datos de la guía
                for d in detalles:
                    calc_subtotal = round(float(d.cantidad or d.volumen_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((d.cantidad or d.volumen_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal
                    inv = InventarioTransitorio(
                        id_guia_inventario_transitorio=guia_header.id_guia_inventario_transitorio,
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
                        subtotal=calc_subtotal,
                        volumen=d.volumen,
                        volumen_eq=d.volumen_eq,
                        precio_eq=d.precio_eq,
                        fecha_recepcion=g_fecha,
                        numero_guia=g_num_guia,
                        numero_proforma=g_num_pf,
                        url_documento=g_url_doc,
                        observaciones=g_obs,
                        estado="RECIBIDO",
                    )
                    db.add(inv)
                    created_items.append(inv)
    else:
        # Caso 2: Recepción simple / legacy (un solo bloque de items)
        guia_header = GuiaInventarioTransitorio(
            numero_guia=top_numero_guia,
            numero_proforma=top_numero_pf,
            id_orden_compra=oc.id_orden_compra,
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
            num_guia = item_override.numero_guia if (item_override and item_override.numero_guia) else top_numero_guia
            num_pf = (item_override and item_override.numero_proforma) or top_numero_pf
            etq = item_override and item_override.etiqueta
            pqs = item_override and item_override.numero_paquetes
            doc = (item_override and item_override.url_documento) or top_url_doc

            esp = item_override.espesor if (item_override and item_override.espesor is not None) else d.espesor
            anc = item_override.ancho if (item_override and item_override.ancho is not None) else d.ancho
            lar = item_override.largo if (item_override and item_override.largo is not None) else d.largo
            txt = item_override.texto_abierto if (item_override and item_override.texto_abierto is not None) else d.texto_abierto
            calc_subtotal = round(float(cant or vol_eq or 0) * float(d.precio_unitario or d.precio_eq or 0), 2) if ((cant or vol_eq) and (d.precio_unitario or d.precio_eq)) else d.subtotal

            inv = InventarioTransitorio(
                id_guia_inventario_transitorio=guia_header.id_guia_inventario_transitorio,
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
                subtotal=calc_subtotal,
                volumen=vol,
                volumen_eq=vol_eq,
                precio_eq=d.precio_eq,
                piezas=pzs,
                fecha_recepcion=fecha_rec,
                numero_guia=num_guia,
                numero_proforma=num_pf,
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

    return [InventarioTransitorioRead(**item.to_dict()) for item in created_items]


@router.post(
    "/guia/documento",
    summary="Subir documento anexo para una Guía de Despacho",
    description="Sube un archivo (PDF, imagen, etc.) y lo asocia a todas las entradas con ese numero_guia."
)
def upload_documento_guia(
    numero_guia: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not numero_guia or not numero_guia.strip():
        raise HTTPException(status_code=400, detail="Debe especificar un número de guía.")
    
    clean_guia = numero_guia.strip()
    headers = db.query(GuiaInventarioTransitorio).filter(GuiaInventarioTransitorio.numero_guia == clean_guia).all()
    items = db.query(InventarioTransitorio).filter(InventarioTransitorio.numero_guia == clean_guia).all()

    static_path = os.path.join(os.getcwd(), "app", "static", "documentos_guias")
    os.makedirs(static_path, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_guia = clean_guia.replace("/", "_").replace("\\", "_")
    unique_filename = f"guia_{safe_guia}_{timestamp}{file_extension}"
    file_path = os.path.join(static_path, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
        
    url_documento = f"/static/documentos_guias/{unique_filename}"
    
    for h in headers:
        h.url_documento = url_documento
    for item in items:
        item.url_documento = url_documento
    db.commit()
    
    return {"ok": True, "numero_guia": clean_guia, "url_documento": url_documento}


@router.delete(
    "/guia/{guia_id}",
    summary="DELETE Eliminar Guía de Despacho e Ítems",
    description="Elimina la guía de despacho por ID y todos sus ítems asociados."
)
def delete_guia_inventario_transitorio(guia_id: int, db: Session = Depends(get_db)):
    guia = db.query(GuiaInventarioTransitorio).filter(GuiaInventarioTransitorio.id_guia_inventario_transitorio == guia_id).first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía de inventario transitorio no encontrada.")

    db.delete(guia)
    db.commit()
    return {"ok": True, "message": f"Guía #{guia_id} y sus productos eliminados exitosamente."}


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
