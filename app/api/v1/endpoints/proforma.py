from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, func, select, literal_column, cast, Numeric, String, case
from typing import List, Optional
from io import BytesIO
import os
import shutil
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from app.db.session import get_db
from app.models.proforma import Proforma
from app.models.detalle_proforma import DetalleProforma
from app.models.orden_compra import OrdenCompra
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.orden_servicio import OrdenServicio
from app.models.detalle_orden_servicio import DetalleOrdenServicio
from app.models.empresa import Empresa
from app.models.moneda import Moneda
from app.models.forma_pago import FormaPago
from app.models.estado_proforma import EstadoProforma
from app.models.usuario import User
from app.models.direccion import Direccion
from app.models.cliente_proveedor import ClienteProveedor
from app.models.operacion_exportacion import OperacionExportacion
from app.models.puerto import Puerto
from app.models.contacto_proforma import ContactoProforma
from app.models.contacto import Contacto
from app.schemas.proforma import ProformaCreate, ProformaRead, ProformaUpdate, ProformaDetailRead
from app.schemas.pagination import create_paginated_response, create_paginated_response_model
from app.services.pdf_generator import ProformaPDFGenerator

# Crear el modelo de respuesta paginada para Proforma
PaginatedProformaResponse = create_paginated_response_model(ProformaRead)

router = APIRouter(prefix="/proforma", tags=["proforma"])


@router.post("/", response_model=ProformaRead, status_code=201, summary='POST Proforma', description='Crear una nueva proforma.')
def create_proforma(payload: ProformaCreate, db: Session = Depends(get_db)):
    # Validar que no exista ya una proforma para esta operación de exportación
    existing_proforma = db.query(Proforma).filter(
        Proforma.id_operacion_exportacion == payload.id_operacion_exportacion
    ).first()
    
    if existing_proforma:
        raise HTTPException(
            status_code=409, 
            detail=f"Ya existe una proforma (ID: {existing_proforma.id_proforma}) para esta operación de exportación."
        )
    
    obj = Proforma(
        id_operacion_exportacion=payload.id_operacion_exportacion,
        id_contenedor=payload.id_contenedor,
        id_usuario_encargado=payload.id_usuario_encargado,
        id_estado_proforma=payload.id_estado_proforma,
        id_moneda=payload.id_moneda,
        id_agente=payload.id_agente,
        id_tipo_comision=payload.id_tipo_comision,
        id_clausula_venta=payload.id_clausula_venta,
        #id_forma_pago=payload.id_forma_pago,
        cantidad_contenedor=payload.cantidad_contenedor,
        fecha_emision=payload.fecha_emision,
        fecha_aceptacion=payload.fecha_aceptacion,
        fecha_entrega=payload.fecha_entrega,
        valor_flete=payload.valor_flete,
        especificaciones=payload.especificaciones,
        nota=payload.nota,
        nota_1=payload.nota_1,
        nota_2=payload.nota_2,
        url_imagen=payload.url_imagen,
        id_empresa=payload.id_empresa,
        id_direccion_facturar=payload.id_direccion_facturar,
        id_direccion_consignar=payload.id_direccion_consignar,
        id_direccion_notificar=payload.id_direccion_notificar,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {
        **{k: v for k, v in obj.__dict__.items() if not k.startswith("_")},
        "id": obj.id_proforma,
        "numero_proforma": obj.id_proforma,
        "numeroProforma": obj.id_proforma,
    }


@router.get("/", response_model=PaginatedProformaResponse, summary='GET Proforma', description='Obtener lista de proformas con paginación.')
def list_proforma(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(Proforma).count()
    
    # Subconsulta para volumen total de proforma (forzamos String antes de replace por si acaso)
    volumen_total_sub = db.query(
        DetalleProforma.id_proforma,
        func.sum(cast(func.coalesce(func.replace(cast(DetalleProforma.volumen_eq, String), ',', '.'), '0'), Numeric(12, 3))).label("vol_total")
    ).group_by(DetalleProforma.id_proforma).subquery()

    # Subconsulta para volumen total por OC (Numeric(12, 3) ya es numérico)
    volumen_per_oc_sub = db.query(
        DetalleOrdenCompra.id_orden_compra,
        func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, 0)).label("vol_oc")
    ).group_by(DetalleOrdenCompra.id_orden_compra).subquery()

    # Subconsulta para volumen asignado y conteo de OCs por Proforma
    # cnt_oc: cuenta TODAS las asociadas (normales o vinculadas)
    # vol_asig: suma SOLO las normales (vinculado IS NULL o != 1)
    oc_summary_sub = db.query(
        OrdenCompra.id_proforma,
        func.count(OrdenCompra.id_orden_compra).label("cnt_oc"),
        func.sum(
            case(
                (func.coalesce(OrdenCompra.vinculado, 0) != 1, func.coalesce(volumen_per_oc_sub.c.vol_oc, 0)),
                else_=0
            )
        ).label("vol_asig")
    ).outerjoin(volumen_per_oc_sub, OrdenCompra.id_orden_compra == volumen_per_oc_sub.c.id_orden_compra)\
     .group_by(OrdenCompra.id_proforma).subquery()

    # Subconsulta para volumen producido por OS provenientes de OCs directas/asignadas.
    os_direct_sub = db.query(
        OrdenCompra.id_proforma.label("id_proforma"),
        func.sum(func.coalesce(DetalleOrdenServicio.volumen_eq, 0)).label("vol_os_direct"),
    ).join(
        OrdenServicio,
        OrdenServicio.id_orden_compra == OrdenCompra.id_orden_compra,
    ).join(
        DetalleOrdenServicio,
        DetalleOrdenServicio.id_orden_servicio == OrdenServicio.id_orden_servicio,
    ).filter(
        func.coalesce(OrdenCompra.vinculado, 0) == 1,
    ).group_by(
        OrdenCompra.id_proforma,
    ).subquery()

    # Alias para joins de direcciones (facturar) y datos de OE
    DirFacturar = aliased(Direccion)
    CPFacturar = aliased(ClienteProveedor)
    CPConsignar = aliased(ClienteProveedor)
    CPNotificar = aliased(ClienteProveedor)
    PuertoOrigenAlias = aliased(Puerto)
    PuertoDestinoAlias = aliased(Puerto)
    OE = aliased(OperacionExportacion)

    # Consulta principal con joins para etiquetas
    query = db.query(
        Proforma,
        func.coalesce(volumen_total_sub.c.vol_total, 0).label("volumenTotal"),
        func.coalesce(oc_summary_sub.c.vol_asig, 0).label("volumenDesdeOc"),
        func.coalesce(os_direct_sub.c.vol_os_direct, 0).label("volumenDesdeOs"),
        func.coalesce(oc_summary_sub.c.cnt_oc, 0).label("oc_asociadas"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        EstadoProforma.nombre.label("estado_nombre"),
        User.nombre.label("usuario_nombre"),
        FormaPago.nombre.label("forma_pago_nombre"),
        CPFacturar.razon_social.label("facturar_a_nombre"),
        CPConsignar.razon_social.label("consignar_a_nombre"),
        CPNotificar.razon_social.label("notificar_a_nombre"),
        DirFacturar.id_cliente_proveedor.label("facturar_a"),
        OE.consignar_a.label("consignar_a"),
        OE.notificar_a.label("notificar_a"),
        PuertoOrigenAlias.nombre.label("puerto_origen_nombre"),
        PuertoDestinoAlias.nombre.label("puerto_destino_nombre"),
        OE.id_puerto_origen.label("id_puerto_origen"),
        OE.id_puerto_destino.label("id_puerto_destino"),
        OE.id_forma_pago.label("id_forma_pago"),
        OE.id_operacion_exportacion.label("id_operacion_exportacion"),
        OE.id_operacion_exportacion.label("oe_numero"),
        FormaPago.nombre.label("formaPago"),
        PuertoOrigenAlias.nombre.label("puertoOrigen"),
        PuertoDestinoAlias.nombre.label("puertoDestino")
    ).outerjoin(volumen_total_sub, Proforma.id_proforma == volumen_total_sub.c.id_proforma)\
     .outerjoin(oc_summary_sub, Proforma.id_proforma == oc_summary_sub.c.id_proforma)\
        .outerjoin(os_direct_sub, Proforma.id_proforma == os_direct_sub.c.id_proforma)\
     .outerjoin(Empresa, Proforma.id_empresa == Empresa.id_empresa)\
     .outerjoin(Moneda, Proforma.id_moneda == Moneda.id_moneda)\
     .outerjoin(EstadoProforma, Proforma.id_estado_proforma == EstadoProforma.id_estado_proforma)\
     .outerjoin(User, Proforma.id_usuario_encargado == User.id_usuario)\
     .outerjoin(OE, Proforma.id_operacion_exportacion == OE.id_operacion_exportacion)\
    .outerjoin(FormaPago, OE.id_forma_pago == FormaPago.id_forma_pago)\
     .outerjoin(DirFacturar, Proforma.id_direccion_facturar == DirFacturar.id_direccion)\
     .outerjoin(CPFacturar, DirFacturar.id_cliente_proveedor == CPFacturar.id_cliente_proveedor)\
     .outerjoin(CPConsignar, OE.consignar_a == CPConsignar.id_cliente_proveedor)\
     .outerjoin(CPNotificar, OE.notificar_a == CPNotificar.id_cliente_proveedor)\
     .outerjoin(PuertoOrigenAlias, OE.id_puerto_origen == PuertoOrigenAlias.id_puerto)\
     .outerjoin(PuertoDestinoAlias, OE.id_puerto_destino == PuertoDestinoAlias.id_puerto)\
     .order_by(desc(Proforma.id_proforma))\
     .offset(skip).limit(page_size)

    results = query.all()
    
    items = []
    for row in results:
        proforma = row[0]
        vol_total = float(row[1] or 0)
        vol_oc = float(row[2] or 0)
        vol_os = float(row[3] or 0)
        vol_abast = vol_oc + vol_os
        oc_cnt = int(row[4] or 0)
        
        # Calcular campos adicionales
        vol_pend = vol_total - vol_abast
        
        estado_flujo = 'sin-oc'
        if oc_cnt == 0:
            estado_flujo = 'sin-oc'
        elif vol_pend < 0.01:
            estado_flujo = 'completado'
        else:
            estado_flujo = 'parcial'
            
        # Convertir a esquema ProformaRead
        item_dict = proforma.__dict__.copy()
        item_dict.update({
            "volumenTotal": vol_total,
            "volumenAsignado": vol_abast,
            "volumenAbastecido": vol_abast,
            "volumenDesdeOc": vol_oc,
            "volumenDesdeOs": vol_os,
            "volumenPendiente": vol_pend,
            "oc_asociadas": oc_cnt,
            "estadoFlujo": estado_flujo,
            "empresa_nombre": row[5],
            "moneda_nombre": row[6],
            "estado_nombre": row[7],
            "usuario_nombre": str(row[8]) if row[8] else None,
            "forma_pago_nombre": str(row[9]) if row[9] else None,
            "facturar_a_nombre": str(row[10]) if row[10] else None,
            "consignar_a_nombre": str(row[11]) if row[11] else None,
            "notificar_a_nombre": str(row[12]) if row[12] else None,
            "facturar_a": row[13],
            "consignar_a": row[14],
            "notificar_a": row[15],
            "id_cliente_facturar": row[13],
            "id_cliente_consignar": row[14],
            "id_cliente_notificar": row[15],
            "puerto_origen_nombre": row[16],
            "puerto_destino_nombre": row[17],
            "id_puerto_origen": row[18],
            "id_puerto_destino": row[19],
            "id_forma_pago": row[20],
            "id_operacion_exportacion": row[21],
            "oe_numero": row[21],
            "numero_operacion": row[21],
            "id": proforma.id_proforma,
            "numero_proforma": proforma.id_proforma,
            "numeroProforma": proforma.id_proforma,
            "formaPago": row[23],
            "puertoOrigen": row[24],
            "puertoDestino": row[25],
            "totalDinero": proforma.valor_flete
        })
        items.append(item_dict)
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/search", response_model=PaginatedProformaResponse, summary='Buscar Proformas', description='Buscar proformas por ID de proforma, ID de operación de exportación, usuario encargado o campo facturar a.')
def search_proforma(
    id_proforma: Optional[int] = Query(None, description="Filtrar por ID de proforma"),
    id_operacion_exportacion: Optional[int] = Query(None, description="Filtrar por ID de operación de exportación"),
    id_usuario_encargado: Optional[int] = Query(None, description="Filtrar por ID de usuario encargado"),
    facturar_a: Optional[str] = Query(None, description="Buscar por razón social del cliente a facturar (búsqueda parcial)"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size

    # Subconsulta volumen total por proforma
    volumen_total_sub = db.query(
        DetalleProforma.id_proforma,
        func.sum(cast(func.coalesce(func.replace(cast(DetalleProforma.volumen_eq, String), ',', '.'), '0'), Numeric(12, 3))).label("vol_total")
    ).group_by(DetalleProforma.id_proforma).subquery()

    # Subconsulta volumen total por OC
    volumen_per_oc_sub = db.query(
        DetalleOrdenCompra.id_orden_compra,
        func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, 0)).label("vol_oc")
    ).group_by(DetalleOrdenCompra.id_orden_compra).subquery()

    # Subconsulta volumen asignado y conteo de OCs por proforma
    oc_summary_sub = db.query(
        OrdenCompra.id_proforma,
        func.count(OrdenCompra.id_orden_compra).label("cnt_oc"),
        func.sum(
            case(
                (func.coalesce(OrdenCompra.vinculado, 0) != 1, func.coalesce(volumen_per_oc_sub.c.vol_oc, 0)),
                else_=0
            )
        ).label("vol_asig")
    ).outerjoin(volumen_per_oc_sub, OrdenCompra.id_orden_compra == volumen_per_oc_sub.c.id_orden_compra)\
     .group_by(OrdenCompra.id_proforma).subquery()

    os_direct_sub = db.query(
        OrdenCompra.id_proforma.label("id_proforma"),
        func.sum(func.coalesce(DetalleOrdenServicio.volumen_eq, 0)).label("vol_os_direct"),
    ).join(
        OrdenServicio,
        OrdenServicio.id_orden_compra == OrdenCompra.id_orden_compra,
    ).join(
        DetalleOrdenServicio,
        DetalleOrdenServicio.id_orden_servicio == OrdenServicio.id_orden_servicio,
    ).filter(
        func.coalesce(OrdenCompra.vinculado, 0) == 1,
    ).group_by(
        OrdenCompra.id_proforma,
    ).subquery()

    DirFacturar = aliased(Direccion)
    CPFacturar = aliased(ClienteProveedor)
    CPConsignar = aliased(ClienteProveedor)
    CPNotificar = aliased(ClienteProveedor)
    PuertoOrigenAlias = aliased(Puerto)
    PuertoDestinoAlias = aliased(Puerto)
    OE = aliased(OperacionExportacion)

    base_query = db.query(
        Proforma,
        func.coalesce(volumen_total_sub.c.vol_total, 0).label("volumenTotal"),
        func.coalesce(oc_summary_sub.c.vol_asig, 0).label("volumenDesdeOc"),
        func.coalesce(os_direct_sub.c.vol_os_direct, 0).label("volumenDesdeOs"),
        func.coalesce(oc_summary_sub.c.cnt_oc, 0).label("oc_asociadas"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        EstadoProforma.nombre.label("estado_nombre"),
        User.nombre.label("usuario_nombre"),
        FormaPago.nombre.label("forma_pago_nombre"),
        CPFacturar.razon_social.label("facturar_a_nombre"),
        CPConsignar.razon_social.label("consignar_a_nombre"),
        CPNotificar.razon_social.label("notificar_a_nombre"),
        DirFacturar.id_cliente_proveedor.label("facturar_a"),
        OE.consignar_a.label("consignar_a"),
        OE.notificar_a.label("notificar_a"),
        PuertoOrigenAlias.nombre.label("puerto_origen_nombre"),
        PuertoDestinoAlias.nombre.label("puerto_destino_nombre"),
        OE.id_puerto_origen.label("id_puerto_origen"),
        OE.id_puerto_destino.label("id_puerto_destino"),
        OE.id_forma_pago.label("id_forma_pago"),
        OE.id_operacion_exportacion.label("id_operacion_exportacion"),
        OE.id_operacion_exportacion.label("oe_numero"),
        FormaPago.nombre.label("formaPago"),
        PuertoOrigenAlias.nombre.label("puertoOrigen"),
        PuertoDestinoAlias.nombre.label("puertoDestino")
    ).outerjoin(volumen_total_sub, Proforma.id_proforma == volumen_total_sub.c.id_proforma)\
     .outerjoin(oc_summary_sub, Proforma.id_proforma == oc_summary_sub.c.id_proforma)\
        .outerjoin(os_direct_sub, Proforma.id_proforma == os_direct_sub.c.id_proforma)\
     .outerjoin(Empresa, Proforma.id_empresa == Empresa.id_empresa)\
     .outerjoin(Moneda, Proforma.id_moneda == Moneda.id_moneda)\
     .outerjoin(EstadoProforma, Proforma.id_estado_proforma == EstadoProforma.id_estado_proforma)\
     .outerjoin(User, Proforma.id_usuario_encargado == User.id_usuario)\
     .outerjoin(OE, Proforma.id_operacion_exportacion == OE.id_operacion_exportacion)\
    .outerjoin(FormaPago, OE.id_forma_pago == FormaPago.id_forma_pago)\
     .outerjoin(DirFacturar, Proforma.id_direccion_facturar == DirFacturar.id_direccion)\
     .outerjoin(CPFacturar, DirFacturar.id_cliente_proveedor == CPFacturar.id_cliente_proveedor)\
     .outerjoin(CPConsignar, OE.consignar_a == CPConsignar.id_cliente_proveedor)\
     .outerjoin(CPNotificar, OE.notificar_a == CPNotificar.id_cliente_proveedor)\
     .outerjoin(PuertoOrigenAlias, OE.id_puerto_origen == PuertoOrigenAlias.id_puerto)\
     .outerjoin(PuertoDestinoAlias, OE.id_puerto_destino == PuertoDestinoAlias.id_puerto)

    # Aplicar filtros
    if id_proforma is not None:
        base_query = base_query.filter(Proforma.id_proforma == id_proforma)
    if id_operacion_exportacion is not None:
        base_query = base_query.filter(Proforma.id_operacion_exportacion == id_operacion_exportacion)
    if id_usuario_encargado is not None:
        base_query = base_query.filter(Proforma.id_usuario_encargado == id_usuario_encargado)
    if facturar_a is not None:
        base_query = base_query.filter(CPFacturar.razon_social.ilike(f"%{facturar_a}%"))

    total_items = base_query.count()

    results = base_query.order_by(desc(Proforma.id_proforma))\
                        .offset(skip).limit(page_size).all()

    items = []
    for row in results:
        proforma = row[0]
        vol_total = float(row[1] or 0)
        vol_oc = float(row[2] or 0)
        vol_os = float(row[3] or 0)
        vol_abast = vol_oc + vol_os
        oc_cnt = int(row[4] or 0)
        vol_pend = vol_total - vol_abast
        if oc_cnt == 0:
            estado_flujo = 'sin-oc'
        elif vol_pend < 0.01:
            estado_flujo = 'completado'
        else:
            estado_flujo = 'parcial'
        item_dict = proforma.__dict__.copy()
        item_dict.update({
            "volumenTotal": vol_total,
            "volumenAsignado": vol_abast,
            "volumenAbastecido": vol_abast,
            "volumenDesdeOc": vol_oc,
            "volumenDesdeOs": vol_os,
            "volumenPendiente": vol_pend,
            "oc_asociadas": oc_cnt,
            "estadoFlujo": estado_flujo,
            "empresa_nombre": row[5],
            "moneda_nombre": row[6],
            "estado_nombre": row[7],
            "usuario_nombre": str(row[8]) if row[8] else None,
            "forma_pago_nombre": str(row[9]) if row[9] else None,
            "facturar_a_nombre": str(row[10]) if row[10] else None,
            "consignar_a_nombre": str(row[11]) if row[11] else None,
            "notificar_a_nombre": str(row[12]) if row[12] else None,
            "facturar_a": row[13],
            "consignar_a": row[14],
            "notificar_a": row[15],
            "id_cliente_facturar": row[13],
            "id_cliente_consignar": row[14],
            "id_cliente_notificar": row[15],
            "puerto_origen_nombre": row[16],
            "puerto_destino_nombre": row[17],
            "id_puerto_origen": row[18],
            "id_puerto_destino": row[19],
            "id_forma_pago": row[20],
            "id_operacion_exportacion": row[21],
            "oe_numero": row[21],
            "numero_operacion": row[21],
            "id": proforma.id_proforma,
            "numero_proforma": proforma.id_proforma,
            "numeroProforma": proforma.id_proforma,
            "formaPago": row[23],
            "puertoOrigen": row[24],
            "puertoDestino": row[25],
            "totalDinero": proforma.valor_flete
        })
        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ProformaDetailRead, summary='GET Proforma', description='Obtener una proforma específica por ID con detalles embebidos.')
def get_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")

    def _cliente_nombre_from_direccion(direccion_obj):
        if not direccion_obj:
            return None
        cliente = getattr(direccion_obj, "ClienteProveedor", None)
        if not cliente:
            return None
        return getattr(cliente, "razon_social", None)

    oe = item.OperacionExportacion

    # Resumen de volumenes para mantener compatibilidad con vistas actuales.
    volumen_total = db.query(
        func.coalesce(
            func.sum(
                cast(
                    func.coalesce(
                        func.replace(cast(DetalleProforma.volumen_eq, String), ',', '.'),
                        '0',
                    ),
                    Numeric(12, 3),
                )
            ),
            0,
        )
    ).filter(DetalleProforma.id_proforma == item_id).scalar() or 0

    volumen_desde_oc = db.query(
        func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
    ).join(
        OrdenCompra,
        OrdenCompra.id_orden_compra == DetalleOrdenCompra.id_orden_compra,
    ).filter(
        OrdenCompra.id_proforma == item_id,
        func.coalesce(OrdenCompra.vinculado, 0) != 1,
    ).scalar() or 0

    volumen_desde_os = db.query(
        func.coalesce(func.sum(DetalleOrdenServicio.volumen_eq), 0)
    ).join(
        OrdenServicio,
        OrdenServicio.id_orden_servicio == DetalleOrdenServicio.id_orden_servicio,
    ).join(
        OrdenCompra,
        OrdenCompra.id_orden_compra == OrdenServicio.id_orden_compra,
    ).filter(
        OrdenCompra.id_proforma == item_id,
        func.coalesce(OrdenCompra.vinculado, 0) == 1,
    ).scalar() or 0

    oc_asociadas = db.query(func.count(OrdenCompra.id_orden_compra)).filter(
        OrdenCompra.id_proforma == item_id
    ).scalar() or 0

    def _q2(value) -> Decimal:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    vol_total_f = _q2(volumen_total)
    vol_oc_f = _q2(volumen_desde_oc)
    vol_os_f = _q2(volumen_desde_os)
    vol_abast_f = _q2(vol_oc_f + vol_os_f)
    vol_pend_f = _q2(vol_total_f - vol_abast_f)

    estado_flujo = 'sin-oc'
    if oc_asociadas == 0:
        estado_flujo = 'sin-oc'
    elif vol_pend_f < 0.01:
        estado_flujo = 'completado'
    else:
        estado_flujo = 'parcial'

    detalles = db.query(DetalleProforma).filter(
        DetalleProforma.id_proforma == item_id
    ).all()

    detalles_payload = []
    for d in detalles:
        producto = getattr(d, "Producto", None)
        especie = getattr(producto, "especie", None) if producto else None
        detalles_payload.append({
            "id_detalle_proforma": d.id_detalle_proforma,
            "id_producto": d.id_producto,
            "especie_nombre": getattr(especie, "nombre_esp", None),
            "producto_nombre": (
                getattr(producto, "nombre_producto_esp", None)
                or getattr(producto, "nombre_producto_ing", None)
                if producto else None
            ),
            "texto_libre": d.texto_libre,
            "id_unidad_venta": d.id_unidad_venta,
            "cantidad": d.cantidad,
            "espesor": d.espesor,
            "id_unidad_medida_espesor": d.id_unidad_medida_espesor,
            "ancho": d.ancho,
            "id_unidad_medida_ancho": d.id_unidad_medida_ancho,
            "largo": d.largo,
            "id_unidad_medida_largo": d.id_unidad_medida_largo,
            "piezas": d.piezas,
            "precio_unitario": d.precio_unitario,
            "subtotal": d.subtotal,
            "volumen_eq": _q2(d.volumen_eq),
            "precio_eq": d.precio_eq,
        })

    ocs = db.query(OrdenCompra).filter(OrdenCompra.id_proforma == item_id).all()
    oc_ids = [oc.id_orden_compra for oc in ocs]
    vol_rows = []
    if oc_ids:
        vol_rows = db.query(
            DetalleOrdenCompra.id_orden_compra,
            func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0).label("volumen_total"),
        ).filter(
            DetalleOrdenCompra.id_orden_compra.in_(oc_ids)
        ).group_by(
            DetalleOrdenCompra.id_orden_compra
        ).all()
    vol_by_oc = {row.id_orden_compra: row.volumen_total for row in vol_rows}

    ordenes_payload = []
    ordenes_servicio_payload = []
    for oc in ocs:
        proveedor = getattr(oc, "ClienteProveedor", None)
        estado_odc = getattr(oc, "EstadoOdc", None)
        os_payload_for_oc = []

        os_rows = []
        if int(getattr(oc, "vinculado", 0) or 0) == 1:
            os_rows = db.query(
                OrdenServicio.id_orden_servicio,
                OrdenServicio.id_estado_orden_servicio,
                func.coalesce(func.sum(DetalleOrdenServicio.volumen_eq), 0).label("volumen_producido"),
            ).outerjoin(
                DetalleOrdenServicio,
                DetalleOrdenServicio.id_orden_servicio == OrdenServicio.id_orden_servicio,
            ).filter(
                OrdenServicio.id_orden_compra == oc.id_orden_compra,
            ).group_by(
                OrdenServicio.id_orden_servicio,
                OrdenServicio.id_estado_orden_servicio,
            ).all()

            for os_row in os_rows:
                estado_os_nombre = db.query(OrdenServicio).get(os_row.id_orden_servicio)
                estado_os = getattr(estado_os_nombre, "EstadoOrdenServicio", None) if estado_os_nombre else None
                os_payload = {
                    "id_orden_servicio": os_row.id_orden_servicio,
                    "id_estado_orden_servicio": os_row.id_estado_orden_servicio,
                    "estado_nombre": getattr(estado_os, "nombre", None),
                    "volumenProducido": _q2(os_row.volumen_producido),
                }
                os_payload_for_oc.append(os_payload)
                ordenes_servicio_payload.append(os_payload)

        ordenes_payload.append({
            "id_orden_compra": oc.id_orden_compra,
            "proveedor_nombre": getattr(proveedor, "razon_social", None),
            "fecha_emision": oc.fecha_emision,
            "volumenTotal": _q2(vol_by_oc.get(oc.id_orden_compra, 0)),
            "estado_nombre": getattr(estado_odc, "nombre", None),
            "id_estado_odc": oc.id_estado_odc,
            "vinculado": oc.vinculado,
            "tipo": "Directa/Asignada" if int(getattr(oc, "vinculado", 0) or 0) == 1 else "Normal",
            "ordenes_servicio": os_payload_for_oc,
        })

    contactos_rows = db.query(Contacto).join(
        ContactoProforma,
        ContactoProforma.id_contacto == Contacto.id_contacto,
    ).filter(
        ContactoProforma.id_proforma == item_id
    ).all()
    contactos_payload = [{
        "id_contacto": c.id_contacto,
        "nombre": c.nombre,
        "correo": c.correo,
        "telefono": c.telefono,
    } for c in contactos_rows]

    payload = {k: v for k, v in item.__dict__.items() if not k.startswith("_")}
    payload.update({
        "volumenTotal": vol_total_f,
        "volumenAsignado": vol_abast_f,
        "volumenAbastecido": vol_abast_f,
        "volumenDesdeOc": vol_oc_f,
        "volumenDesdeOs": vol_os_f,
        "volumenPendiente": vol_pend_f,
        "oc_asociadas": int(oc_asociadas),
        "estadoFlujo": estado_flujo,
        "empresa_nombre": getattr(item.Empresa, "nombre_fantasia", None),
        "moneda_nombre": getattr(item.Moneda, "etiqueta", None) if getattr(item, "Moneda", None) else None,
        "estado_nombre": getattr(item.EstadoProforma, "nombre", None) if getattr(item, "EstadoProforma", None) else None,
        "usuario_nombre": getattr(item.UsuarioEncargado, "nombre", None) if getattr(item, "UsuarioEncargado", None) else None,
        "id_operacion_exportacion": getattr(oe, "id_operacion_exportacion", None),
        "oe_numero": getattr(oe, "id_operacion_exportacion", None),
        "numero_operacion": getattr(oe, "id_operacion_exportacion", None),
        "id": item.id_proforma,
        "numero_proforma": item.id_proforma,
        "numeroProforma": item.id_proforma,
        "facturar_a": getattr(oe, "facturar_a", None) if oe else None,
        "consignar_a": getattr(oe, "consignar_a", None) if oe else None,
        "notificar_a": getattr(oe, "notificar_a", None) if oe else None,
        "id_cliente_facturar": getattr(oe, "facturar_a", None) if oe else None,
        "id_cliente_consignar": getattr(oe, "consignar_a", None) if oe else None,
        "id_cliente_notificar": getattr(oe, "notificar_a", None) if oe else None,
        "facturar_a_nombre": (
            getattr(getattr(oe, "FacturarA", None), "razon_social", None)
            if oe else _cliente_nombre_from_direccion(item.DireccionFacturar)
        ),
        "consignar_a_nombre": (
            getattr(getattr(oe, "ConsignarA", None), "razon_social", None)
            if oe else _cliente_nombre_from_direccion(item.DireccionConsignar)
        ),
        "notificar_a_nombre": (
            getattr(getattr(oe, "NotificarA", None), "razon_social", None)
            if oe else _cliente_nombre_from_direccion(item.DireccionNotificar)
        ),
        "facturar_a_id": getattr(oe, "facturar_a", None) if oe else None,
        "consignar_a_id": getattr(oe, "consignar_a", None) if oe else None,
        "notificar_a_id": getattr(oe, "notificar_a", None) if oe else None,
        "facturar_a_cliente": getattr(oe, "FacturarA", None) if oe else None,
        "consignar_a_cliente": getattr(oe, "ConsignarA", None) if oe else None,
        "notificar_a_cliente": getattr(oe, "NotificarA", None) if oe else None,
        "direccion_facturar": getattr(item, "DireccionFacturar", None),
        "direccion_consignar": getattr(item, "DireccionConsignar", None),
        "direccion_notificar": getattr(item, "DireccionNotificar", None),
        "puerto_origen_nombre": getattr(getattr(oe, "PuertoOrigen", None), "nombre", None) if oe else None,
        "puerto_destino_nombre": getattr(getattr(oe, "PuertoDestino", None), "nombre", None) if oe else None,
        "puerto_origen": getattr(oe, "PuertoOrigen", None) if oe else None,
        "puerto_destino": getattr(oe, "PuertoDestino", None) if oe else None,
        "forma_pago_nombre": getattr(getattr(oe, "FormaPago", None), "nombre", None) if oe else None,
        "id_puerto_origen": getattr(oe, "id_puerto_origen", None) if oe else None,
        "id_puerto_destino": getattr(oe, "id_puerto_destino", None) if oe else None,
        "id_forma_pago": getattr(oe, "id_forma_pago", None) if oe else None,
        "agente_nombre": getattr(item.Agente, "nombre", None) if getattr(item, "Agente", None) else None,
        "tipo_comision_nombre": getattr(item.TipoComision, "nombre", None) if getattr(item, "TipoComision", None) else None,
        "clausula_venta_nombre": item.id_clausula_venta,
        "detalles": detalles_payload,
        "ordenes_compra": ordenes_payload,
        "ordenes_servicio": ordenes_servicio_payload,
        "contactos": contactos_payload,
    })
    return payload


@router.put("/{item_id}", response_model=ProformaRead, summary='PUT Proforma', description='Actualizar una proforma existente.')
def update_proforma(item_id: int, payload: ProformaUpdate, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        **{k: v for k, v in item.__dict__.items() if not k.startswith("_")},
        "id": item.id_proforma,
        "numero_proforma": item.id_proforma,
        "numeroProforma": item.id_proforma,
    }


@router.delete("/{item_id}", summary='DELETE Proforma', description='Eliminar una proforma.')
def delete_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    
    # Verificar si tiene órdenes de compra asociadas
    ordenes_actuales = item.OrdenesCompra.count()
    ordenes_anteriores = item.OrdenesCompraAnterior.count()
    
    if ordenes_actuales > 0 or ordenes_anteriores > 0:
        total_ordenes = ordenes_actuales + ordenes_anteriores
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la proforma porque tiene {total_ordenes} orden(es) de compra asociada(s)"
        )
    
    # Verificar si tiene detalles de proforma
    detalles_count = item.DetalleProforma.count()
    if detalles_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la proforma porque tiene {detalles_count} detalle(s) asociado(s)"
        )
    
    # Verificar si tiene contactos de proforma
    contactos_count = item.ContactosProforma.count()
    if contactos_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar la proforma porque tiene {contactos_count} contacto(s) asociado(s)"
        )
    
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.post("/{item_id}/imagen", summary='Subir imagen de la proforma', description='Sube una imagen para asociarla a la proforma.')
def upload_imagen_proforma(item_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Sube una imagen para la proforma y actualiza el campo url_imagen.
    """
    # Verificar que la proforma existe
    proforma = db.get(Proforma, item_id)
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma no encontrada")
    
    # Validar que sea una imagen
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Crear el directorio si no existe
    static_path = os.path.join(os.getcwd(), "app", "static", "imagenes_proforma")
    os.makedirs(static_path, exist_ok=True)
    
    # Generar nombre único para el archivo
    file_extension = os.path.splitext(file.filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"proforma_{item_id}_{timestamp}{file_extension}"
    file_path = os.path.join(static_path, unique_filename)
    
    # Guardar el archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Actualizar la URL de la imagen en la base de datos
    url_imagen = f"/static/imagenes_proforma/{unique_filename}"
    proforma.url_imagen = url_imagen
    db.add(proforma)
    db.commit()
    db.refresh(proforma)
    
    return {
        "message": "Imagen subida exitosamente",
        "url_imagen": url_imagen,
        "filename": unique_filename
    }


@router.get("/{item_id}/pdf/spanish", summary='Descargar PDF Proforma Español', description='Descarga la proforma en formato PDF en español.')
def get_proforma_pdf_spanish(item_id: int, db: Session = Depends(get_db)):
    """Genera y descarga el PDF de la proforma en español"""
    proforma = db.get(Proforma, item_id)
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma not found")
    
    try:
        generator = ProformaPDFGenerator(language='es')
        pdf_buffer = generator.generate_pdf(proforma, db)
        pdf_buffer.seek(0)
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Proforma_{item_id}_ES.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@router.get("/{item_id}/pdf/english", summary='Descargar PDF Proforma Inglés', description='Descarga la proforma en formato PDF en inglés.')
def get_proforma_pdf_english(item_id: int, db: Session = Depends(get_db)):
    """Genera y descarga el PDF de la proforma en inglés"""
    proforma = db.get(Proforma, item_id)
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma not found")
    
    try:
        generator = ProformaPDFGenerator(language='en')
        pdf_buffer = generator.generate_pdf(proforma, db)
        pdf_buffer.seek(0)
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Proforma_{item_id}_EN.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@router.get("/{item_id}/pdf", summary='Descargar PDF Proforma', description='Descarga ambos PDFs (español e inglés) de la proforma.')
def get_proforma_pdf_both(item_id: int, language: str = Query('es', description='Idioma del PDF (es, en)'), db: Session = Depends(get_db)):
    """Genera y descarga el PDF de la proforma en el idioma solicitado"""
    proforma = db.get(Proforma, item_id)
    if not proforma:
        raise HTTPException(status_code=404, detail="Proforma not found")
    
    lang = language.lower() if language.lower() in ['es', 'en'] else 'es'
    lang_suffix = 'ES' if lang == 'es' else 'EN'
    
    try:
        generator = ProformaPDFGenerator(language=lang)
        pdf_buffer = generator.generate_pdf(proforma, db)
        pdf_buffer.seek(0)
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=Proforma_{item_id}_{lang_suffix}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
