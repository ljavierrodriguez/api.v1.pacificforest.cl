from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from app.models.detalle_orden_servicio import DetalleOrdenServicio
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, cast, String, or_
from typing import Optional
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import os
import shutil
from datetime import datetime
from app.db.session import get_db
from app.models.detalle_orden_servicio import DetalleOrdenServicio
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.contacto_orden_servicio import ContactoOrdenServicio
from app.models.orden_servicio import OrdenServicio
from app.models.cliente_proveedor import ClienteProveedor
from app.models.usuario import User
from app.models.moneda import Moneda
from app.models.empresa import Empresa
from app.models.estado_orden_servicio import EstadoOrdenServicio
from pydantic import BaseModel
from app.models.orden_compra import OrdenCompra
from app.models.detalle_proforma import DetalleProforma
from app.schemas.orden_servicio import OrdenServicioCreate, OrdenServicioRead, OrdenServicioUpdate,  AsignarOrdenCompraPayload
from app.schemas.pagination import create_paginated_response, create_paginated_response_model
from app.services.pdf_generator import OrdenServicioPDFGenerator

PaginatedOrdenServicioResponse = create_paginated_response_model(OrdenServicioRead)

router = APIRouter(prefix="/orden_servicio", tags=["orden_servicio"])

VOLUME_TOLERANCE_PCT = Decimal("0.10")
VOLUME_EPSILON = Decimal("0.001")


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _is_directa(vinculado_value) -> bool:
    try:
        return int(vinculado_value or 0) == 1
    except (ValueError, TypeError):
        return False


def _get_os_volume_by_id(db: Session, os_id: int) -> Decimal:
    vol = db.query(
        func.coalesce(func.sum(DetalleOrdenServicio.volumen_eq), 0)
    ).filter(
        DetalleOrdenServicio.id_orden_servicio == os_id,
    ).scalar()
    return _to_decimal(vol)


def _validate_os_volume_against_proforma(
    db: Session,
    orden_compra: OrdenCompra,
    nueva_os_volumen: Decimal,
    current_os_id: Optional[int] = None,
) -> None:
    if not orden_compra or orden_compra.id_proforma is None:
        return

    if not _is_directa(getattr(orden_compra, "vinculado", None)):
        return

    proforma_id = orden_compra.id_proforma

    volumen_proforma_total = db.query(
        func.coalesce(func.sum(func.coalesce(DetalleProforma.volumen_eq, 0)), 0)
    ).filter(
        DetalleProforma.id_proforma == proforma_id,
    ).scalar()

    volumen_ocs_normales = db.query(
        func.coalesce(func.sum(DetalleOrdenCompra.volumen_eq), 0)
    ).join(
        OrdenCompra,
        DetalleOrdenCompra.id_orden_compra == OrdenCompra.id_orden_compra,
    ).filter(
        OrdenCompra.id_proforma == proforma_id,
        func.coalesce(OrdenCompra.vinculado, 0) != 1,
    ).scalar()

    volumen_os_directas = db.query(
        func.coalesce(func.sum(DetalleOrdenServicio.volumen_eq), 0)
    ).join(
        OrdenServicio,
        DetalleOrdenServicio.id_orden_servicio == OrdenServicio.id_orden_servicio,
    ).join(
        OrdenCompra,
        OrdenServicio.id_orden_compra == OrdenCompra.id_orden_compra,
    ).filter(
        OrdenCompra.id_proforma == proforma_id,
        func.coalesce(OrdenCompra.vinculado, 0) == 1,
    )

    if current_os_id is not None:
        volumen_os_directas = volumen_os_directas.filter(
            OrdenServicio.id_orden_servicio != current_os_id,
        )

    volumen_os_directas = volumen_os_directas.scalar()

    proforma_dec = _to_decimal(volumen_proforma_total)
    ocs_normales_dec = _to_decimal(volumen_ocs_normales)
    os_directas_dec = _to_decimal(volumen_os_directas)
    nueva_os_dec = _to_decimal(nueva_os_volumen)

    volumen_maximo_permitido = proforma_dec * (Decimal("1") + VOLUME_TOLERANCE_PCT)
    abastecido_post = ocs_normales_dec + os_directas_dec + nueva_os_dec

    if abastecido_post > (volumen_maximo_permitido + VOLUME_EPSILON):
        raise HTTPException(
            status_code=403,
            detail=(
                "El volumen producido por la orden de servicio excede el maximo permitido "
                f"de la proforma ({volumen_maximo_permitido.quantize(Decimal('0.001'))})"
            ),
        )


def _round_volume(value, decimals: int = 2) -> Decimal:
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


@router.post("/", response_model=OrdenServicioRead, status_code=201)
def create_orden_servicio(payload: OrdenServicioCreate, db: Session = Depends(get_db)):
    if not payload.detalles or len(payload.detalles) == 0:
        raise HTTPException(
            status_code=400,
            detail="La orden de servicio debe tener al menos 1 detalle",
        )

    proveedor = db.get(ClienteProveedor, payload.id_cliente_proveedor)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    if not proveedor.es_proveedor:
        raise HTTPException(status_code=400, detail="El cliente/proveedor seleccionado no es proveedor")

    oc_asociada = None
    if payload.id_orden_compra is not None:
        oc_asociada = db.get(OrdenCompra, payload.id_orden_compra)
        if not oc_asociada:
            raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

        volumen_payload = sum(_to_decimal(detalle.volumen_eq) for detalle in payload.detalles)
        _validate_os_volume_against_proforma(
            db=db,
            orden_compra=oc_asociada,
            nueva_os_volumen=volumen_payload,
            current_os_id=None,
        )

    obj = OrdenServicio(
        fecha_emision=payload.fecha_emision,
        fecha_entrega=payload.fecha_entrega,
        id_cliente_proveedor=payload.id_cliente_proveedor,
        id_usuario_encargado=payload.id_usuario_encargado,
        id_usuario=payload.id_usuario,
        servicio=payload.servicio,
        destino=payload.destino,
        id_moneda=payload.id_moneda,
        id_empresa=payload.id_empresa,
        id_direccion_proveedor=payload.id_direccion_proveedor,
        observacion=payload.observacion,
        nota_1=payload.nota_1,
        otras_especificaciones=payload.otras_especificaciones,
        url_imagen=payload.url_imagen,
        valor_neto=payload.valor_neto,
        iva=payload.iva,
        tasa_iva=payload.tasa_iva,
        valor_total=payload.valor_total,
        flete=payload.flete,
        id_estado_orden_servicio=payload.id_estado_orden_servicio,
        id_orden_compra=payload.id_orden_compra,
    )
    db.add(obj)
    db.flush()

    for detalle in payload.detalles:
        det_dict = detalle.model_dump(exclude_unset=True)
        det_dict.pop("id_especie", None)
        detalle_obj = DetalleOrdenServicio(
            id_orden_servicio=obj.id_orden_servicio,
            **det_dict,
        )
        db.add(detalle_obj)


    if payload.contactos_orden_servicio:
        for contacto in payload.contactos_orden_servicio:
            contacto_obj = ContactoOrdenServicio(
                id_orden_servicio=obj.id_orden_servicio,
                id_contacto=contacto.id_contacto,
        )
            db.add(contacto_obj)    

    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedOrdenServicioResponse)
def list_orden_servicio(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
):
    skip = (page - 1) * page_size

    base_query = db.query(OrdenServicio)
    total_items = base_query.count()

    volumen_sub = db.query(
        DetalleOrdenServicio.id_orden_servicio,
        func.sum(func.coalesce(DetalleOrdenServicio.volumen_eq, 0)).label("vol_total")
    ).group_by(DetalleOrdenServicio.id_orden_servicio).subquery()

    query = db.query(
        OrdenServicio,
        func.coalesce(volumen_sub.c.vol_total, 0).label("volumenTotal"),
        ClienteProveedor.razon_social.label("proveedor_nombre"),
        User.nombre.label("usuario_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        EstadoOrdenServicio.nombre.label("estado_nombre"),
    ).outerjoin(volumen_sub, OrdenServicio.id_orden_servicio == volumen_sub.c.id_orden_servicio)\
     .outerjoin(ClienteProveedor, OrdenServicio.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor)\
     .outerjoin(User, OrdenServicio.id_usuario_encargado == User.id_usuario)\
     .outerjoin(Moneda, OrdenServicio.id_moneda == Moneda.id_moneda)\
     .outerjoin(Empresa, OrdenServicio.id_empresa == Empresa.id_empresa)\
     .outerjoin(EstadoOrdenServicio, OrdenServicio.id_estado_orden_servicio == EstadoOrdenServicio.id_estado_orden_servicio)
    query = query.order_by(desc(OrdenServicio.id_orden_servicio)).offset(skip).limit(page_size)
    results = query.all()

    items = []
    for row in results:
        item = row[0]
        item_dict = item.__dict__.copy()
        item_dict.update({
            "volumenTotal": _round_volume(row.volumenTotal),
            "proveedor_nombre": row.proveedor_nombre,
            "usuario_nombre": row.usuario_nombre,
            "moneda_nombre": row.moneda_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
            "orden_compra_numero": item.id_orden_compra,
        })
        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


@router.get("/search", response_model=PaginatedOrdenServicioResponse)
def search_orden_servicio(
    id_orden_servicio: Optional[int] = Query(None),
    id_orden_compra: Optional[int] = Query(None),
    id_cliente_proveedor: Optional[int] = Query(None),
    id_estado_orden_servicio: Optional[int] = Query(None),
    id_empresa: Optional[int] = Query(None),
    id_moneda: Optional[int] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    proveedor: Optional[str] = Query(None),
    usuario_encargado: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size

    volumen_sub = db.query(
        DetalleOrdenServicio.id_orden_servicio,
        func.sum(func.coalesce(DetalleOrdenServicio.volumen_eq, 0)).label("vol_total")
    ).group_by(DetalleOrdenServicio.id_orden_servicio).subquery()

    base_query = db.query(
        OrdenServicio,
        func.coalesce(volumen_sub.c.vol_total, 0).label("volumenTotal"),
        ClienteProveedor.razon_social.label("proveedor_nombre"),
        User.nombre.label("usuario_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        EstadoOrdenServicio.nombre.label("estado_nombre"),
    ).outerjoin(volumen_sub, OrdenServicio.id_orden_servicio == volumen_sub.c.id_orden_servicio)\
     .outerjoin(ClienteProveedor, OrdenServicio.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor)\
     .outerjoin(User, OrdenServicio.id_usuario_encargado == User.id_usuario)\
     .outerjoin(Moneda, OrdenServicio.id_moneda == Moneda.id_moneda)\
     .outerjoin(Empresa, OrdenServicio.id_empresa == Empresa.id_empresa)\
     .outerjoin(EstadoOrdenServicio, OrdenServicio.id_estado_orden_servicio == EstadoOrdenServicio.id_estado_orden_servicio)

    search_term = query or q or proveedor
    if search_term and search_term.strip():
        st = f"%{search_term.strip()}%"
        base_query = base_query.filter(
            or_(
                cast(OrdenServicio.id_orden_servicio, String).ilike(st),
                cast(OrdenServicio.id_orden_compra, String).ilike(st),
                OrdenServicio.servicio.ilike(st),
                OrdenServicio.destino.ilike(st),
                ClienteProveedor.razon_social.ilike(st),
                ClienteProveedor.nombre_fantasia.ilike(st),
                User.nombre.ilike(st),
                EstadoOrdenServicio.nombre.ilike(st),
                Empresa.nombre_fantasia.ilike(st),
            )
        )

    if id_orden_servicio is not None:
        base_query = base_query.filter(OrdenServicio.id_orden_servicio == id_orden_servicio)
    if id_orden_compra is not None:
        base_query = base_query.filter(OrdenServicio.id_orden_compra == id_orden_compra)
    if id_cliente_proveedor is not None:
        base_query = base_query.filter(OrdenServicio.id_cliente_proveedor == id_cliente_proveedor)
    if id_estado_orden_servicio is not None:
        base_query = base_query.filter(OrdenServicio.id_estado_orden_servicio == id_estado_orden_servicio)
    if id_empresa is not None:
        base_query = base_query.filter(OrdenServicio.id_empresa == id_empresa)
    if id_moneda is not None:
        base_query = base_query.filter(OrdenServicio.id_moneda == id_moneda)

    if fecha_desde and fecha_desde.strip():
        try:
            d_desde = datetime.strptime(fecha_desde.strip().split("T")[0], "%Y-%m-%d").date()
            base_query = base_query.filter(func.date(OrdenServicio.fecha_emision) >= d_desde)
        except Exception:
            pass

    if fecha_hasta and fecha_hasta.strip():
        try:
            d_hasta = datetime.strptime(fecha_hasta.strip().split("T")[0], "%Y-%m-%d").date()
            base_query = base_query.filter(func.date(OrdenServicio.fecha_emision) <= d_hasta)
        except Exception:
            pass

    if usuario_encargado and usuario_encargado.strip() and not search_term:
        base_query = base_query.filter(User.nombre.ilike(f"%{usuario_encargado.strip()}%"))

    total_items = base_query.count()

    results = base_query.order_by(desc(OrdenServicio.id_orden_servicio)).offset(skip).limit(page_size).all()

    items = []
    for row in results:
        item = row[0]
        item_dict = item.__dict__.copy()
        item_dict.update({
            "volumenTotal": _round_volume(row.volumenTotal),
            "proveedor_nombre": row.proveedor_nombre,
            "usuario_nombre": row.usuario_nombre,
            "moneda_nombre": row.moneda_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
            "orden_compra_numero": item.id_orden_compra,
        })
        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


@router.patch("/{item_id}/asignar-orden-compra", response_model=OrdenServicioRead)
def asignar_orden_compra_a_servicio(
    item_id: int,
    payload: AsignarOrdenCompraPayload,
    db: Session = Depends(get_db)
):
    orden_servicio = db.get(OrdenServicio, item_id)
    if not orden_servicio:
        raise HTTPException(status_code=404, detail="Orden de servicio no encontrada")

    orden_compra = db.get(OrdenCompra, payload.id_orden_compra)
    if not orden_compra:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

    volumen_os = _get_os_volume_by_id(db, item_id)
    _validate_os_volume_against_proforma(
        db=db,
        orden_compra=orden_compra,
        nueva_os_volumen=volumen_os,
        current_os_id=item_id,
    )


    orden_servicio.id_orden_compra = payload.id_orden_compra

    db.add(orden_servicio)
    db.commit()
    db.refresh(orden_servicio)

    return orden_servicio    


@router.get("/{item_id}", response_model=OrdenServicioRead)
def get_orden_servicio(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenServicio not found")

    volumen_total = db.query(
        func.coalesce(func.sum(DetalleOrdenServicio.volumen_eq), 0)
    ).filter(
        DetalleOrdenServicio.id_orden_servicio == item_id
    ).scalar()

    os_dict = item.serialize() if hasattr(item, 'serialize') else dict(item.__dict__)
    os_dict["volumenTotal"] = _round_volume(volumen_total)
    os_dict["flete"] = float(item.flete) if item.flete is not None else 0

    proveedor = getattr(item, "ClienteProveedor", None)
    usuario = getattr(item, "UsuarioEncargado", None)
    moneda = getattr(item, "Moneda", None)
    empresa = getattr(item, "Empresa", None)
    estado = getattr(item, "EstadoOrdenServicio", None)

    os_dict["proveedor_nombre"] = getattr(proveedor, "razon_social", None)
    os_dict["usuario_nombre"] = getattr(usuario, "nombre", None)
    os_dict["moneda_nombre"] = getattr(moneda, "etiqueta", None)
    os_dict["empresa_nombre"] = getattr(empresa, "nombre_fantasia", None)
    os_dict["estado_nombre"] = getattr(estado, "nombre", None)
    os_dict["orden_compra_numero"] = item.id_orden_compra

    detalles_servicio = []
    detalles_list = item.DetalleOrdenServicio.all() if item.DetalleOrdenServicio is not None else []
    for d in detalles_list:
        producto = getattr(d, "Producto", None)
        especie = getattr(producto, "especie", None)
        unidad_venta = getattr(d, "UnidadVenta", None)
        um_espesor = getattr(d, "UnidadMedidaEspesor", None)
        um_ancho = getattr(d, "UnidadMedidaAncho", None)
        um_largo = getattr(d, "UnidadMedidaLargo", None)
        detalles_servicio.append({
            "id_detalle_os": d.id_detalle_os,
            "id_orden_servicio": d.id_orden_servicio,
            "id_producto": d.id_producto,
            "id_especie": getattr(producto, "id_especie", None),
            "especie_nombre": getattr(especie, "nombre_esp", None),
            "id_unidad_venta": d.id_unidad_venta,
            "texto_abierto": d.texto_abierto,
            "espesor": d.espesor,
            "id_unidad_medida_espesor": d.id_unidad_medida_espesor,
            "ancho": d.ancho,
            "id_unidad_medida_ancho": d.id_unidad_medida_ancho,
            "largo": d.largo,
            "id_unidad_medida_largo": d.id_unidad_medida_largo,
            "cantidad": float(d.cantidad) if d.cantidad is not None else None,
            "precio_unitario": float(d.precio_unitario),
            "subtotal": float(d.subtotal) if d.subtotal is not None else None,
            "volumen": float(d.volumen) if d.volumen is not None else None,
            "volumen_eq": float(d.volumen_eq) if d.volumen_eq is not None else None,
            "precio_eq": float(d.precio_eq) if d.precio_eq is not None else None,
            "producto_nombre": getattr(producto, "nombre_producto_esp", None),
            "unidad_venta_nombre": getattr(unidad_venta, "nombre", None),
            "unidad_medida_espesor_nombre": getattr(um_espesor, "nombre", None),
            "unidad_medida_ancho_nombre": getattr(um_ancho, "nombre", None),
            "unidad_medida_largo_nombre": getattr(um_largo, "nombre", None),
        })
    os_dict["detalles_orden_servicio"] = detalles_servicio

    contactos_list = item.ContactosOrdenServicio.all() if item.ContactosOrdenServicio is not None else []
    contactos_servicio = []
    for c in contactos_list:
        contacto = getattr(c, "Contacto", None)
        contactos_servicio.append({
            "id_contacto_orden_servicio": c.id_contacto_orden_servicio,
            "id_contacto": c.id_contacto,
            "id_orden_servicio": c.id_orden_servicio,
            "contacto_nombre": getattr(contacto, "nombre", None),
            "contacto_correo": getattr(contacto, "correo", None),
            "contacto_telefono": getattr(contacto, "telefono", None),
        })
    os_dict["contactos_orden_servicio"] = contactos_servicio

    return os_dict




@router.put("/{item_id}", response_model=OrdenServicioRead)
def update_orden_servicio(
    item_id: int,
    payload: OrdenServicioUpdate,
    db: Session = Depends(get_db)
):
    item = db.get(OrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenServicio not found")

    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    detalles = data.pop("detalles", None)
    contactos = data.pop("contactos_orden_servicio", None)

    target_oc_id = data.get("id_orden_compra", item.id_orden_compra)

    if target_oc_id is not None:
        oc_asociada = db.get(OrdenCompra, target_oc_id)
        if not oc_asociada:
            raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

        if detalles is not None:
            volumen_nuevo = sum(_to_decimal(detalle.get("volumen_eq")) for detalle in detalles)
        else:
            volumen_nuevo = _get_os_volume_by_id(db, item_id)

        _validate_os_volume_against_proforma(
            db=db,
            orden_compra=oc_asociada,
            nueva_os_volumen=volumen_nuevo,
            current_os_id=item_id,
        )
   

    for k, v in data.items():
        setattr(item, k, v)

    if detalles is not None:
        db.query(DetalleOrdenServicio).filter(
            DetalleOrdenServicio.id_orden_servicio == item_id
        ).delete(synchronize_session=False)
        for detalle in detalles:
            nuevo_detalle = DetalleOrdenServicio(
                id_orden_servicio=item_id,
                id_producto=detalle["id_producto"],
                id_unidad_venta=detalle.get("id_unidad_venta"),
                texto_abierto=detalle.get("texto_abierto"),
                espesor=detalle.get("espesor"),
                id_unidad_medida_espesor=detalle.get("id_unidad_medida_espesor"),
                ancho=detalle.get("ancho"),
                id_unidad_medida_ancho=detalle.get("id_unidad_medida_ancho"),
                largo=detalle.get("largo"),
                id_unidad_medida_largo=detalle.get("id_unidad_medida_largo"),
                cantidad=detalle.get("cantidad"),
                precio_unitario=detalle.get("precio_unitario"),
                subtotal=detalle.get("subtotal"),
                volumen=detalle.get("volumen"),
                volumen_eq=detalle.get("volumen_eq"),
                precio_eq=detalle.get("precio_eq"),
            )
            db.add(nuevo_detalle)

    if contactos is not None:
        db.query(ContactoOrdenServicio).filter(
            ContactoOrdenServicio.id_orden_servicio == item_id
        ).delete(synchronize_session=False)
        for contacto in contactos:
            nuevo_contacto = ContactoOrdenServicio(
                id_orden_servicio=item_id,
                id_contacto=contacto["id_contacto"],
            )
            db.add(nuevo_contacto)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_orden_servicio(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenServicio not found")

    detalles_count = db.query(DetalleOrdenServicio).filter(
        DetalleOrdenServicio.id_orden_servicio == item_id
    ).count()

    if detalles_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar la orden de servicio porque tiene {detalles_count} detalle(s) asociado(s)"
        )

    db.delete(item)
    db.commit()
    return {"ok": True}


@router.post("/{item_id}/imagen")
def upload_imagen_orden_servicio(item_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    orden_servicio = db.get(OrdenServicio, item_id)
    if not orden_servicio:
        raise HTTPException(status_code=404, detail="Orden de servicio no encontrada")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    static_path = os.path.join(os.getcwd(), "app", "static", "imagenes_orden_servicio")
    os.makedirs(static_path, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"os_{item_id}_{timestamp}{file_extension}"
    file_path = os.path.join(static_path, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url_imagen = f"/static/imagenes_orden_servicio/{unique_filename}"
    orden_servicio.url_imagen = url_imagen
    db.add(orden_servicio)
    db.commit()
    db.refresh(orden_servicio)

    return {
        "message": "Imagen subida exitosamente",
        "url_imagen": url_imagen,
        "filename": unique_filename
    }


@router.get("/{item_id}/pdf/spanish")
def get_os_pdf_spanish(item_id: int, db: Session = Depends(get_db)):
    orden_servicio = db.get(OrdenServicio, item_id)
    if not orden_servicio:
        raise HTTPException(status_code=404, detail="OrdenServicio not found")

    try:
        generator = OrdenServicioPDFGenerator(language="es")
        pdf_buffer = generator.generate_pdf(orden_servicio, db)
        pdf_buffer.seek(0)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=OrdenServicio_{item_id}_ES.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@router.get("/{item_id}/pdf/english")
def get_os_pdf_english(item_id: int, db: Session = Depends(get_db)):
    orden_servicio = db.get(OrdenServicio, item_id)
    if not orden_servicio:
        raise HTTPException(status_code=404, detail="OrdenServicio not found")

    try:
        generator = OrdenServicioPDFGenerator(language="en")
        pdf_buffer = generator.generate_pdf(orden_servicio, db)
        pdf_buffer.seek(0)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=OrdenServicio_{item_id}_EN.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


@router.get("/{item_id}/pdf")
def get_os_pdf(
    item_id: int,
    language: str = Query("es", description="Idioma del PDF (es, en)"),
    db: Session = Depends(get_db),
):
    orden_servicio = db.get(OrdenServicio, item_id)
    if not orden_servicio:
        raise HTTPException(status_code=404, detail="OrdenServicio not found")

    lang = language.lower() if language.lower() in ("es", "en") else "es"
    lang_suffix = "ES" if lang == "es" else "EN"

    try:
        generator = OrdenServicioPDFGenerator(language=lang)
        pdf_buffer = generator.generate_pdf(orden_servicio, db)
        pdf_buffer.seek(0)
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=OrdenServicio_{item_id}_{lang_suffix}.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")




@router.delete("/{item_id}/imagen")
def delete_imagen_orden_servicio(item_id: int, db: Session = Depends(get_db)):
    orden_servicio = db.get(OrdenServicio, item_id)
    if not orden_servicio:
        raise HTTPException(status_code=404, detail="Orden de servicio no encontrada")

    if not orden_servicio.url_imagen:
        raise HTTPException(status_code=404, detail="La orden de servicio no tiene imagen asociada")

    # Obtener la ruta física del archivo
    imagen_rel_path = orden_servicio.url_imagen.lstrip("/")  # Quitar el primer /
    imagen_abs_path = os.path.join(os.getcwd(), imagen_rel_path)

    # Eliminar el archivo físico si existe
    if os.path.exists(imagen_abs_path):
        try:
            os.remove(imagen_abs_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error eliminando el archivo de imagen: {str(e)}")

    # Limpiar la referencia en la base de datos
    orden_servicio.url_imagen = None
    db.add(orden_servicio)
    db.commit()
    db.refresh(orden_servicio)

    return {"message": "Imagen eliminada exitosamente"}