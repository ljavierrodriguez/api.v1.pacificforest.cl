from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, cast, String, or_
from typing import List, Optional
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.detalle_proforma import DetalleProforma
from app.models.orden_compra import OrdenCompra
from app.models.especie import Especie
from app.models.producto import Producto
from app.models.cliente_proveedor import ClienteProveedor
from app.models.usuario import User
from app.models.moneda import Moneda
from app.models.bodega import Bodega
from app.models.empresa import Empresa
from app.models.estado_odc import EstadoOdc
from app.schemas.orden_compra import OrdenCompraCreate, OrdenCompraRead, OrdenCompraUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model
from app.services.pdf_generator import OrdenCompraPDFGenerator

# Crear el modelo de respuesta paginada para OrdenCompra
PaginatedOrdenCompraResponse = create_paginated_response_model(OrdenCompraRead)

router = APIRouter(prefix="/orden_compra", tags=["orden_compra"])

VOLUME_TOLERANCE_PCT = Decimal("0.10")
VOLUME_EPSILON = Decimal("0.001")


def _is_directa(vinculado_value) -> bool:
    try:
        return int(vinculado_value or 0) == 1
    except (ValueError, TypeError):
        return False


def _round_volume(value, decimals: int = 2) -> Decimal:
    """Round volume values consistently for API responses."""
    if value is None:
        return Decimal("0")
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")

    if decimals <= 0:
        return decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    quantizer = Decimal("1").scaleb(-decimals)
    return decimal_value.quantize(quantizer, rounding=ROUND_HALF_UP)


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _validate_especies_orden_vs_proforma(db: Session, proforma_id: int, orden_compra_id: int) -> None:
    especies_proforma_rows = (
        db.query(Producto.id_especie, Especie.nombre_esp)
        .join(DetalleProforma, DetalleProforma.id_producto == Producto.id_producto)
        .outerjoin(Especie, Especie.id_especie == Producto.id_especie)
        .filter(DetalleProforma.id_proforma == proforma_id)
        .distinct()
        .all()
    )
    especies_orden_rows = (
        db.query(Producto.id_especie, Especie.nombre_esp)
        .join(DetalleOrdenCompra, DetalleOrdenCompra.id_producto == Producto.id_producto)
        .outerjoin(Especie, Especie.id_especie == Producto.id_especie)
        .filter(DetalleOrdenCompra.id_orden_compra == orden_compra_id)
        .distinct()
        .all()
    )

    especies_proforma = {especie_id for especie_id, _ in especies_proforma_rows if especie_id is not None}
    especies_orden = {especie_id for especie_id, _ in especies_orden_rows if especie_id is not None}
    nombre_especie_orden = {
        especie_id: (nombre_esp or "SIN NOMBRE")
        for especie_id, nombre_esp in especies_orden_rows
        if especie_id is not None
    }

    if especies_proforma and not especies_orden:
        raise HTTPException(
            status_code=403,
            detail="La orden no tiene productos con especie válida para vincular a la proforma",
        )

    especies_no_permitidas = especies_orden - especies_proforma
    if especies_no_permitidas:
        especies_no_permitidas_txt = ", ".join(
            sorted(
                nombre_especie_orden.get(especie_id, "SIN NOMBRE")
                for especie_id in especies_no_permitidas
            )
        )
        raise HTTPException(
            status_code=403,
            detail=f"La orden contiene especie(s) que no existen en la proforma: {especies_no_permitidas_txt}",
        )


def _validate_volumen_orden_vs_proforma(db: Session, proforma_id: int, orden_compra_id: int) -> None:
    if not proforma_id:
        return

    volumen_proforma_total = db.query(
        func.coalesce(
            func.sum(func.coalesce(DetalleProforma.volumen_eq, DetalleProforma.cantidad, 0)),
            0,
        )
    ).filter(
        DetalleProforma.id_proforma == proforma_id,
    ).scalar()

    volumen_proforma_total_dec = _to_decimal(volumen_proforma_total)
    volumen_maximo_permitido = volumen_proforma_total_dec * (Decimal("1") + VOLUME_TOLERANCE_PCT)

    volumen_otros_odc = db.query(
        func.coalesce(
            func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, DetalleOrdenCompra.volumen, DetalleOrdenCompra.cantidad, 0)),
            0,
        )
    ).join(
        OrdenCompra,
        DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
    ).filter(
        OrdenCompra.id_proforma == proforma_id,
        OrdenCompra.id_orden_compra != orden_compra_id,
    ).scalar()

    volumen_otros_odc_dec = _to_decimal(volumen_otros_odc)

    volumen_actual_odc = db.query(
        func.coalesce(
            func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, DetalleOrdenCompra.volumen, DetalleOrdenCompra.cantidad, 0)),
            0,
        )
    ).filter(
        DetalleOrdenCompra.id_orden_compra == orden_compra_id,
    ).scalar()

    volumen_actual_odc_dec = _to_decimal(volumen_actual_odc)
    volumen_total_acumulado = volumen_otros_odc_dec + volumen_actual_odc_dec

    disponible_para_esta_oc = volumen_maximo_permitido - volumen_otros_odc_dec
    if disponible_para_esta_oc < Decimal("0"):
        disponible_para_esta_oc = Decimal("0")

    if volumen_total_acumulado > (volumen_maximo_permitido + VOLUME_EPSILON):
        if disponible_para_esta_oc <= VOLUME_EPSILON:
            raise HTTPException(
                status_code=403,
                detail=f"El volumen de la proforma PF-{proforma_id} ya fue completado ({volumen_otros_odc_dec.quantize(Decimal('0.001'))} m³ de {volumen_proforma_total_dec.quantize(Decimal('0.001'))} m³ + 10% tol).",
            )
        raise HTTPException(
            status_code=403,
            detail=(
                f"El volumen total acumulado de las órdenes de compra ({volumen_total_acumulado.quantize(Decimal('0.001'))} m³) "
                f"supera el máximo permitido para la proforma PF-{proforma_id} "
                f"({volumen_maximo_permitido.quantize(Decimal('0.001'))} m³ = {volumen_proforma_total_dec.quantize(Decimal('0.001'))} m³ + 10% tolerancia). "
                f"Volumen máximo disponible para esta orden: {disponible_para_esta_oc.quantize(Decimal('0.001'))} m³."
            ),
        )


@router.post("/", response_model=OrdenCompraRead, status_code=201, summary='POST OrdenCompra', description='Crear una nueva orden de compra.')
def create_orden_compra(payload: OrdenCompraCreate, db: Session = Depends(get_db)):
    # Validar que detalles no esté vacío
    if not payload.detalles or len(payload.detalles) == 0:
        raise HTTPException(
            status_code=400,
            detail="La orden de compra debe tener al menos 1 detalle",
        )

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

    for detalle in payload.detalles:
        detalle_dict = detalle.model_dump(exclude_unset=True)
        if detalle_dict.get("subtotal") is None:
            cant = float(detalle_dict.get("cantidad") or 0)
            pu = float(detalle_dict.get("precio_unitario") or 0)
            detalle_dict["subtotal"] = round(cant * pu, 3)
        detalle_obj = DetalleOrdenCompra(
            id_orden_compra=obj.id_orden_compra,
            **detalle_dict,
        )
        db.add(detalle_obj)
    db.flush()

    # Validar productos y volumen acumulado contra la proforma siempre que exista id_proforma
    if payload.id_proforma:
        _validate_especies_orden_vs_proforma(db, payload.id_proforma, obj.id_orden_compra)
        _validate_volumen_orden_vs_proforma(db, payload.id_proforma, obj.id_orden_compra)

    db.commit()
    db.refresh(obj)
    return obj


from app.models.proforma import Proforma
from app.models.operacion_exportacion import OperacionExportacion

# ... (omitting other imports)

@router.get("/", response_model=PaginatedOrdenCompraResponse, summary='GET OrdenCompra', description='Obtener lista de órdenes de compra con paginación.')
def list_orden_compra(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    id_proforma: Optional[int] = Query(None, description="Filtrar por ID de proforma")
):
    skip = (page - 1) * page_size

    # Construir filtro base
    base_query = db.query(OrdenCompra)
    if id_proforma is not None:
        base_query = base_query.filter(OrdenCompra.id_proforma == id_proforma)

    # Obtener total de elementos
    total_items = base_query.count()
    
    # Subconsulta para volumen total por OC
    volumen_sub = db.query(
        DetalleOrdenCompra.id_orden_compra,
        func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, 0)).label("vol_total")
    ).group_by(DetalleOrdenCompra.id_orden_compra).subquery()

    # Consulta principal con joins para etiquetas
    query = db.query(
        OrdenCompra,
        func.coalesce(volumen_sub.c.vol_total, 0).label("volumenTotal"),
        ClienteProveedor.razon_social.label("proveedor_nombre"),
        User.nombre.label("usuario_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        Bodega.nombre.label("bodega_nombre"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        EstadoOdc.nombre.label("estado_nombre"),
        OperacionExportacion.id_operacion_exportacion.label("id_operacion_exportacion")
    ).outerjoin(volumen_sub, OrdenCompra.id_orden_compra == volumen_sub.c.id_orden_compra)\
     .outerjoin(ClienteProveedor, OrdenCompra.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor)\
     .outerjoin(User, OrdenCompra.id_usuario_encargado == User.id_usuario)\
     .outerjoin(Moneda, OrdenCompra.id_moneda == Moneda.id_moneda)\
     .outerjoin(Bodega, OrdenCompra.id_bodega == Bodega.id_bodega)\
     .outerjoin(Empresa, OrdenCompra.id_empresa == Empresa.id_empresa)\
     .outerjoin(EstadoOdc, OrdenCompra.id_estado_odc == EstadoOdc.id_estado_odc)\
     .outerjoin(Proforma, OrdenCompra.id_proforma == Proforma.id_proforma)\
     .outerjoin(OperacionExportacion, Proforma.id_operacion_exportacion == OperacionExportacion.id_operacion_exportacion)

    if id_proforma is not None:
        query = query.filter(OrdenCompra.id_proforma == id_proforma)

    query = query.order_by(desc(OrdenCompra.id_orden_compra))\
     .offset(skip).limit(page_size)

    results = query.all()
    
    items = []
    for row in results:
        oc = row[0]
        item_dict = oc.__dict__.copy()
        item_dict.update({
            "volumenTotal": _round_volume(row.volumenTotal),
            "proveedor_nombre": row.proveedor_nombre,
            "usuario_nombre": row.usuario_nombre,
            "moneda_nombre": row.moneda_nombre,
            "bodega_nombre": row.bodega_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
            "id_operacion_exportacion": row.id_operacion_exportacion,
            "tipo": "Asignada" if oc.id_proforma else "Directa",
        })
        items.append(item_dict)
    
    return create_paginated_response(items, page, page_size, total_items)

@router.get(
    "/search",
    response_model=PaginatedOrdenCompraResponse,
    summary="Buscar Órdenes de Compra",
    description="Buscar órdenes de compra por coincidencia parcial de N° OC, N° proforma, N° OE, proveedor o usuario encargado.",
)
def search_orden_compra(
    query: Optional[str] = Query(None, description="Búsqueda parcial por N° OC"),
    id_orden_compra: Optional[int] = Query(None, description="Filtrar por N° exacto de orden de compra"),
    id_proforma: Optional[int] = Query(None, description="Filtrar por N° de proforma"),
    id_operacion_exportacion: Optional[int] = Query(None, description="Filtrar por N° de operación de exportación"),
    proveedor: Optional[str] = Query(None, description="Buscar por razón social del proveedor"),
    usuario_encargado: Optional[str] = Query(None, description="Buscar por nombre del usuario encargado"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size

    volumen_sub = db.query(
        DetalleOrdenCompra.id_orden_compra,
        func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, 0)).label("vol_total")
    ).group_by(DetalleOrdenCompra.id_orden_compra).subquery()

    base_query = db.query(
        OrdenCompra,
        func.coalesce(volumen_sub.c.vol_total, 0).label("volumenTotal"),
        ClienteProveedor.razon_social.label("proveedor_nombre"),
        User.nombre.label("usuario_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        Bodega.nombre.label("bodega_nombre"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        EstadoOdc.nombre.label("estado_nombre"),
        OperacionExportacion.id_operacion_exportacion.label("id_operacion_exportacion"),
    ).outerjoin(
        volumen_sub, OrdenCompra.id_orden_compra == volumen_sub.c.id_orden_compra
    ).outerjoin(
        ClienteProveedor, OrdenCompra.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor
    ).outerjoin(
        User, OrdenCompra.id_usuario_encargado == User.id_usuario
    ).outerjoin(
        Moneda, OrdenCompra.id_moneda == Moneda.id_moneda
    ).outerjoin(
        Bodega, OrdenCompra.id_bodega == Bodega.id_bodega
    ).outerjoin(
        Empresa, OrdenCompra.id_empresa == Empresa.id_empresa
    ).outerjoin(
        EstadoOdc, OrdenCompra.id_estado_odc == EstadoOdc.id_estado_odc
    ).outerjoin(
        Proforma, OrdenCompra.id_proforma == Proforma.id_proforma
    ).outerjoin(
        OperacionExportacion, Proforma.id_operacion_exportacion == OperacionExportacion.id_operacion_exportacion
    )

    if query:
        search_term = f"%{query.strip()}%"
        base_query = base_query.filter(
            or_(
                cast(OrdenCompra.id_orden_compra, String).ilike(search_term),
                cast(OrdenCompra.id_proforma, String).ilike(search_term),
                ClienteProveedor.razon_social.ilike(search_term),
                ClienteProveedor.nombre_fantasia.ilike(search_term),
                User.nombre.ilike(search_term),
                EstadoOdc.nombre.ilike(search_term),
                Bodega.nombre.ilike(search_term),
                Empresa.nombre_fantasia.ilike(search_term),
            )
        )
    elif id_orden_compra is not None:
        base_query = base_query.filter(
            OrdenCompra.id_orden_compra == id_orden_compra
        )

    if id_proforma is not None:
        base_query = base_query.filter(OrdenCompra.id_proforma == id_proforma)

    if id_operacion_exportacion is not None:
        base_query = base_query.filter(
            OperacionExportacion.id_operacion_exportacion == id_operacion_exportacion
        )

    if proveedor is not None:
        base_query = base_query.filter(
            ClienteProveedor.razon_social.ilike(f"%{proveedor}%")
        )

    if usuario_encargado is not None:
        base_query = base_query.filter(
            User.nombre.ilike(f"%{usuario_encargado}%")
        )

    total_items = base_query.count()

    results = base_query.order_by(desc(OrdenCompra.id_orden_compra))\
        .offset(skip)\
        .limit(page_size)\
        .all()

    items = []
    for row in results:
        oc = row[0]
        item_dict = oc.__dict__.copy()
        item_dict.pop("_sa_instance_state", None)

        item_dict.update({
            "volumenTotal": _round_volume(row.volumenTotal),
            "proveedor_nombre": row.proveedor_nombre,
            "usuario_nombre": row.usuario_nombre,
            "moneda_nombre": row.moneda_nombre,
            "bodega_nombre": row.bodega_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
            "id_operacion_exportacion": row.id_operacion_exportacion,
            "tipo": "Asignada" if oc.id_proforma else "Directa",
        })

        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=OrdenCompraRead, summary='GET OrdenCompra', description='Obtener una orden de compra específica por ID.')
def get_orden_compra(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")

    volumen_total = db.query(
        func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
    ).filter(
        DetalleOrdenCompra.id_orden_compra == item_id
    ).scalar()

    # Serializar la orden de compra
    oc_dict = item.serialize() if hasattr(item, 'serialize') else dict(item.__dict__)
    oc_dict["volumenTotal"] = _round_volume(volumen_total)
    oc_dict["tipo"] = "Asignada" if item.id_proforma else "Directa"

    # Agregar etiquetas si existen
    proveedor = getattr(item, "ClienteProveedor", None)
    usuario = getattr(item, "UsuarioEncargado", None)
    moneda = getattr(item, "Moneda", None)
    bodega = getattr(item, "Bodega", None)
    empresa = getattr(item, "Empresa", None)
    estado = getattr(item, "EstadoOdc", None)
    proforma = getattr(item, "Proforma", None)

    oc_dict["proveedor_nombre"] = getattr(proveedor, "razon_social", None)
    oc_dict["usuario_nombre"] = getattr(usuario, "nombre", None)
    oc_dict["moneda_nombre"] = getattr(moneda, "etiqueta", None)
    oc_dict["bodega_nombre"] = getattr(bodega, "nombre", None)
    oc_dict["empresa_nombre"] = getattr(empresa, "nombre_fantasia", None)
    oc_dict["estado_nombre"] = getattr(estado, "nombre", None)

    # Embebido: proveedor (objeto completo)
    proveedor_obj = None
    if proveedor:
        if hasattr(proveedor, "to_dict"):
            proveedor_obj = proveedor.to_dict()
        else:
            proveedor_obj = dict(proveedor.__dict__)
    oc_dict["proveedor"] = proveedor_obj

    # Embebido: direccion_proveedor (objeto completo)
    direccion_obj = None
    direccion = getattr(item, "DireccionProveedor", None)
    if direccion:
        if hasattr(direccion, "to_dict"):
            direccion_obj = direccion.to_dict()
        else:
            direccion_obj = dict(direccion.__dict__)
    oc_dict["direccion_proveedor"] = direccion_obj


    # Embebido: proforma
    id_operacion_exportacion = None
    if proforma:
        proforma_dict = proforma.serialize() if hasattr(proforma, 'serialize') else dict(proforma.__dict__)

        # Embebido: detalles de proforma
        detalles = []
        if hasattr(proforma, 'DetalleProforma') and proforma.DetalleProforma is not None:
            for det in proforma.DetalleProforma:
                if hasattr(det, 'to_dict'):
                    detalles.append(det.to_dict())
                else:
                    detalles.append(dict(det.__dict__))
        proforma_dict["detalles"] = detalles

        # Embebido: contactos de proforma
        contactos = []
        if hasattr(proforma, 'ContactosProforma') and proforma.ContactosProforma is not None:
            for cp in proforma.ContactosProforma:
                contacto = getattr(cp, 'Contacto', None)
                if contacto:
                    if hasattr(contacto, 'to_dict'):
                        contactos.append(contacto.to_dict())
                    else:
                        contactos.append(dict(contacto.__dict__))
        proforma_dict["contactos"] = contactos

        # Embebido: operacion_exportacion
        oe = getattr(proforma, "OperacionExportacion", None)
        if oe:
            oe_dict = oe.to_dict() if hasattr(oe, 'to_dict') else dict(oe.__dict__)
            # Etiquetas comunes
            oe_dict["puerto_origen_nombre"] = getattr(getattr(oe, "PuertoOrigen", None), "nombre", None)
            oe_dict["puerto_destino_nombre"] = getattr(getattr(oe, "PuertoDestino", None), "nombre", None)
            proforma_dict["operacion_exportacion"] = oe_dict
            # Asignar id_operacion_exportacion principal
            id_operacion_exportacion = getattr(oe, "id_operacion_exportacion", None)
        else:
            proforma_dict["operacion_exportacion"] = None

        oc_dict["proforma"] = proforma_dict
    else:
        oc_dict["proforma"] = None
    # Incluir id_operacion_exportacion principal
    oc_dict["id_operacion_exportacion"] = id_operacion_exportacion

    # Embebido: contactos de la orden de compra
    contactos_orden = []
    if hasattr(item, 'ContactosOrdenCompra') and item.ContactosOrdenCompra is not None:
        contactos_query = item.ContactosOrdenCompra
        contactos_list = contactos_query.all() if hasattr(contactos_query, 'all') else contactos_query
        for c in contactos_list:
            contacto = getattr(c, 'Contacto', None)
            if contacto:
                if hasattr(contacto, 'to_dict'):
                    contactos_orden.append(contacto.to_dict())
                else:
                    contactos_orden.append(dict(contacto.__dict__))
    # Siempre incluir el campo aunque esté vacío
    oc_dict["contactos_orden_compra"] = contactos_orden

    # Embebido: detalles/productos de la orden de compra
    detalles_orden = []
    if hasattr(item, 'DetalleOrdenCompra') and item.DetalleOrdenCompra is not None:
        detalles_query = item.DetalleOrdenCompra
        detalles_list = detalles_query.all() if hasattr(detalles_query, 'all') else detalles_query
        for d in detalles_list:
            if hasattr(d, 'to_dict'):
                detalles_orden.append(d.to_dict())
            else:
                detalles_orden.append(dict(d.__dict__))
    oc_dict["detalles_orden_compra"] = detalles_orden

    return oc_dict


@router.put("/{item_id}", response_model=OrdenCompraRead, summary='PUT OrdenCompra', description='Actualizar una orden de compra existente.')
def update_orden_compra(item_id: int, payload: OrdenCompraUpdate, db: Session = Depends(get_db)):
    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")

    payload_data = payload.model_dump(exclude_unset=True)

    nuevo_id_proforma = payload_data.get("id_proforma", item.id_proforma)
    nuevo_vinculado = payload_data.get("vinculado", item.vinculado)
    es_oc_directa = _is_directa(nuevo_vinculado)

    detalles_data = payload_data.pop("detalles", None)

    for k, v in payload_data.items():
        setattr(item, k, v)
    db.add(item)

    if detalles_data is not None:
        db.query(DetalleOrdenCompra).filter(
            DetalleOrdenCompra.id_orden_compra == item_id
        ).delete(synchronize_session=False)

        for detalle_dict in detalles_data:
            # Remover campos sólo UI si vienen
            detalle_dict.pop("id_especie", None)
            detalle_dict.pop("producto_nombre", None)
            detalle_dict.pop("unidad_venta_nombre", None)
            if detalle_dict.get("subtotal") is None:
                cant = float(detalle_dict.get("cantidad") or 0)
                pu = float(detalle_dict.get("precio_unitario") or 0)
                detalle_dict["subtotal"] = round(cant * pu, 3)
            detalle_obj = DetalleOrdenCompra(
                id_orden_compra=item.id_orden_compra,
                **detalle_dict,
            )
            db.add(detalle_obj)
    db.flush()

    if nuevo_id_proforma:
        _validate_especies_orden_vs_proforma(db, nuevo_id_proforma, item.id_orden_compra)
        _validate_volumen_orden_vs_proforma(db, nuevo_id_proforma, item.id_orden_compra)

    db.commit()
    db.refresh(item)
    return get_orden_compra(item_id, db)


@router.post("/{item_id}/desvincular", response_model=OrdenCompraRead, summary='Desvincular OrdenCompra', description='Desvincula la orden de compra de su proforma y la deja como orden directa (solo admin).')
def desvincular_orden_compra(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if (getattr(current_user, "login", "") or "").strip().lower() != "administrador":
        raise HTTPException(status_code=403, detail="Solo un administrador puede desvincular una orden de compra")

    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")

    if item.id_proforma is None:
        raise HTTPException(status_code=400, detail="La orden de compra ya es directa")

    item.id_proforma_anterior = item.id_proforma
    item.id_proforma = None
    item.vinculado = 0

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _update_proforma_estado(db: Session, proforma_id: int) -> None:
    if not proforma_id:
        return
    from app.models.proforma import Proforma
    from app.models.detalle_proforma import DetalleProforma
    proforma = db.get(Proforma, proforma_id)
    if not proforma:
        return

    volumen_proforma = db.query(
        func.coalesce(func.sum(DetalleProforma.volumen_eq), 0)
    ).filter(DetalleProforma.id_proforma == proforma_id).scalar()

    volumen_odc = db.query(
        func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
    ).join(
        OrdenCompra,
        DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
    ).filter(
        OrdenCompra.id_proforma == proforma_id,
        func.coalesce(OrdenCompra.vinculado, 0) != 1,
    ).scalar()

    if (volumen_odc or 0) == 0:
        proforma.id_estado_proforma = 1
    elif (volumen_odc or 0) >= (volumen_proforma or 0) - 10:
        proforma.id_estado_proforma = 3
    else:
        proforma.id_estado_proforma = 2

    db.add(proforma)


@router.delete("/{item_id}", summary='DELETE OrdenCompra', description='Eliminar una orden de compra.')
def delete_orden_compra(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
    
    try:
        # 1. Verificar si tiene recepciones en Inventario Transitorio
        from app.models.inventario_transitorio import InventarioTransitorio
        transitorio_count = db.query(InventarioTransitorio).filter(
            InventarioTransitorio.id_orden_compra == item_id
        ).count()
        if transitorio_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar la Orden de Compra OC-{item_id} porque tiene {transitorio_count} registro(s) de guía(s) recepcionada(s) en Inventario Transitorio.",
            )

        # 2. Verificar si tiene Órdenes de Servicio asociadas
        from app.models.orden_servicio import OrdenServicio
        os_count = db.query(OrdenServicio).filter(
            OrdenServicio.id_orden_compra == item_id
        ).count()
        if os_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar la Orden de Compra OC-{item_id} porque tiene {os_count} orden(es) de servicio asociada(s).",
            )

        # 3. Verificar si tiene registros PLE asociados
        from app.models.ple import Ple
        ple_count = db.query(Ple).filter(
            Ple.id_orden_compra == item_id
        ).count()
        if ple_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar la Orden de Compra OC-{item_id} porque tiene {ple_count} registro(s) PLE asociado(s).",
            )

        proforma_id = item.id_proforma

        # Eliminar detalles y contactos propios de la OC
        from app.models.detalle_orden_compra import DetalleOrdenCompra
        db.query(DetalleOrdenCompra).filter(
            DetalleOrdenCompra.id_orden_compra == item_id
        ).delete(synchronize_session=False)

        from app.models.contacto_orden_compra import ContactoOrdenCompra
        db.query(ContactoOrdenCompra).filter(
            ContactoOrdenCompra.id_orden_compra == item_id
        ).delete(synchronize_session=False)

        # Eliminar la orden de compra
        db.delete(item)
        db.flush()

        # Recalcular estado de la proforma vinculada
        if proforma_id:
            _update_proforma_estado(db, proforma_id)

        db.commit()
        return {"ok": True, "message": f"Orden de Compra OC-{item_id} eliminada exitosamente"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al eliminar la orden de compra: {str(e)}")


@router.post("/{item_id}/imagen", summary='Subir imagen de la orden de compra', description='Sube una imagen para asociarla a la orden de compra.')
def upload_imagen_orden_compra(item_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Sube una imagen para la orden de compra y actualiza el campo url_imagen.
    """
    # Verificar que la orden de compra existe
    orden_compra = db.get(OrdenCompra, item_id)
    if not orden_compra:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
    
    # Validar que sea una imagen
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Crear el directorio si no existe
    static_path = os.path.join(os.getcwd(), "app", "static", "imagenes_orden_compra")
    os.makedirs(static_path, exist_ok=True)
    
    # Generar nombre único para el archivo
    file_extension = os.path.splitext(file.filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"oc_{item_id}_{timestamp}{file_extension}"
    file_path = os.path.join(static_path, unique_filename)
    
    # Guardar el archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Actualizar la URL de la imagen en la base de datos
    url_imagen = f"/static/imagenes_orden_compra/{unique_filename}"
    orden_compra.url_imagen = url_imagen
    db.add(orden_compra)
    db.commit()
    db.refresh(orden_compra)
    
    return {
        "message": "Imagen subida exitosamente",
        "url_imagen": url_imagen,
        "filename": unique_filename
    }


@router.get("/{item_id}/pdf/spanish", summary='Descargar PDF Orden de Compra Español', description='Descarga la orden de compra en formato PDF en español.')
def get_odc_pdf_spanish(item_id: int, db: Session = Depends(get_db)):
    """Genera y descarga el PDF de la orden de compra en español."""
    orden_compra = db.get(OrdenCompra, item_id)
    if not orden_compra:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")

    try:
        generator = OrdenCompraPDFGenerator(language="es")
        pdf_buffer = generator.generate_pdf(orden_compra, db)
        pdf_buffer.seek(0)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=OrdenCompra_{item_id}_ES.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@router.get("/{item_id}/pdf/english", summary='Descargar PDF Orden de Compra Inglés', description='Descarga la orden de compra en formato PDF en inglés.')
def get_odc_pdf_english(item_id: int, db: Session = Depends(get_db)):
    """Genera y descarga el PDF de la orden de compra en inglés."""
    orden_compra = db.get(OrdenCompra, item_id)
    if not orden_compra:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")

    try:
        generator = OrdenCompraPDFGenerator(language="en")
        pdf_buffer = generator.generate_pdf(orden_compra, db)
        pdf_buffer.seek(0)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=OrdenCompra_{item_id}_EN.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@router.get("/{item_id}/pdf", summary='Descargar PDF Orden de Compra', description='Descarga la orden de compra en formato PDF. Parámetro lang: es (default) o en.')
def get_odc_pdf(
    item_id: int,
    language: str = Query("es", description="Idioma del PDF (es, en)"),
    db: Session = Depends(get_db),
):
    """Genera y descarga el PDF de la orden de compra en el idioma solicitado."""
    orden_compra = db.get(OrdenCompra, item_id)
    if not orden_compra:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")

    lang = language.lower() if language.lower() in ("es", "en") else "es"
    lang_suffix = "ES" if lang == "es" else "EN"

    try:
        generator = OrdenCompraPDFGenerator(language=lang)
        pdf_buffer = generator.generate_pdf(orden_compra, db)
        pdf_buffer.seek(0)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=OrdenCompra_{item_id}_{lang_suffix}.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")