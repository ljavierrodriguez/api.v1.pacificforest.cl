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
    from app.models.bodega import Bodega
    from app.models.producto import Producto

    totals_query = db.query(
        func.coalesce(func.sum(InventarioTransitorio.volumen), 0).label("volumen"),
        func.coalesce(func.sum(InventarioTransitorio.volumen_eq), 0).label("volumen_eq"),
        func.coalesce(func.sum(InventarioTransitorio.subtotal), 0).label("costo"),
        func.count(InventarioTransitorio.id_inventario_transitorio).label("items_count"),
        func.coalesce(func.sum(InventarioTransitorio.numero_paquetes), 0).label("paquetes_count"),
        func.coalesce(func.sum(InventarioTransitorio.piezas), 0).label("piezas_count")
    )
    if id_bodega:
        totals_query = totals_query.filter(InventarioTransitorio.id_bodega == id_bodega)
    t = totals_query.first()

    q_bodega = (
        db.query(
            InventarioTransitorio.id_bodega,
            func.coalesce(Bodega.nombre, "Sin Bodega").label("bodega_nombre"),
            func.coalesce(func.sum(InventarioTransitorio.volumen), 0).label("volumen"),
            func.coalesce(func.sum(InventarioTransitorio.volumen_eq), 0).label("volumen_eq"),
            func.coalesce(func.sum(InventarioTransitorio.subtotal), 0).label("costo"),
            func.count(InventarioTransitorio.id_inventario_transitorio).label("items_count"),
            func.coalesce(func.sum(InventarioTransitorio.numero_paquetes), 0).label("paquetes_count"),
        )
        .outerjoin(Bodega, InventarioTransitorio.id_bodega == Bodega.id_bodega)
    )
    if id_bodega:
        q_bodega = q_bodega.filter(InventarioTransitorio.id_bodega == id_bodega)
    desglose_bodegas = (
        q_bodega.group_by(InventarioTransitorio.id_bodega, Bodega.nombre)
        .order_by(desc("costo"))
        .all()
    )

    q_producto = (
        db.query(
            InventarioTransitorio.id_producto,
            func.coalesce(Producto.nombre_producto_esp, Producto.nombre_producto_ing, InventarioTransitorio.texto_abierto, "Sin Producto").label("producto_nombre"),
            func.coalesce(func.sum(InventarioTransitorio.volumen), 0).label("volumen"),
            func.coalesce(func.sum(InventarioTransitorio.volumen_eq), 0).label("volumen_eq"),
            func.coalesce(func.sum(InventarioTransitorio.subtotal), 0).label("costo"),
            func.count(InventarioTransitorio.id_inventario_transitorio).label("items_count"),
        )
        .outerjoin(Producto, InventarioTransitorio.id_producto == Producto.id_producto)
    )
    if id_bodega:
        q_producto = q_producto.filter(InventarioTransitorio.id_bodega == id_bodega)
    desglose_productos = (
        q_producto.group_by(InventarioTransitorio.id_producto, Producto.nombre_producto_esp, Producto.nombre_producto_ing, InventarioTransitorio.texto_abierto)
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
                        subtotal=d.subtotal,
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
                        subtotal=d.subtotal,
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
                subtotal=d.subtotal,
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
