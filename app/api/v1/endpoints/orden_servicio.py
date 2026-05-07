from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.models.detalle_orden_servicio import DetalleOrdenServicio
from app.models.orden_servicio import OrdenServicio
from app.models.cliente_proveedor import ClienteProveedor
from app.models.usuario import User
from app.models.moneda import Moneda
from app.models.bodega import Bodega
from app.models.empresa import Empresa
from app.models.estado_orden_servicio import EstadoOrdenServicio
from app.schemas.orden_servicio import OrdenServicioCreate, OrdenServicioRead, OrdenServicioUpdate
from app.schemas.pagination import create_paginated_response, create_paginated_response_model
from app.services.pdf_generator import OrdenServicioPDFGenerator

PaginatedOrdenServicioResponse = create_paginated_response_model(OrdenServicioRead)

router = APIRouter(prefix="/orden_servicio", tags=["orden_servicio"])


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

    obj = OrdenServicio(
        fecha_emision=payload.fecha_emision,
        fecha_entrega=payload.fecha_entrega,
        id_cliente_proveedor=payload.id_cliente_proveedor,
        id_usuario_encargado=payload.id_usuario_encargado,
        id_usuario=payload.id_usuario,
        id_bodega=payload.id_bodega,
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
        id_estado_orden_servicio=payload.id_estado_orden_servicio,
    )
    db.add(obj)
    db.flush()

    for detalle in payload.detalles:
        detalle_obj = DetalleOrdenServicio(
            id_orden_servicio=obj.id_orden_servicio,
            **detalle.model_dump(exclude_unset=True),
        )
        db.add(detalle_obj)

    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedOrdenServicioResponse)
def list_orden_servicio(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
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
        Bodega.nombre.label("bodega_nombre"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        EstadoOrdenServicio.nombre.label("estado_nombre"),
    ).outerjoin(volumen_sub, OrdenServicio.id_orden_servicio == volumen_sub.c.id_orden_servicio)\
     .outerjoin(ClienteProveedor, OrdenServicio.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor)\
     .outerjoin(User, OrdenServicio.id_usuario_encargado == User.id_usuario)\
     .outerjoin(Moneda, OrdenServicio.id_moneda == Moneda.id_moneda)\
     .outerjoin(Bodega, OrdenServicio.id_bodega == Bodega.id_bodega)\
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
            "bodega_nombre": row.bodega_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
        })
        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


@router.get("/search", response_model=PaginatedOrdenServicioResponse)
def search_orden_servicio(
    id_orden_servicio: Optional[int] = Query(None),
    proveedor: Optional[str] = Query(None),
    usuario_encargado: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
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
        Bodega.nombre.label("bodega_nombre"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        EstadoOrdenServicio.nombre.label("estado_nombre"),
    ).outerjoin(volumen_sub, OrdenServicio.id_orden_servicio == volumen_sub.c.id_orden_servicio)\
     .outerjoin(ClienteProveedor, OrdenServicio.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor)\
     .outerjoin(User, OrdenServicio.id_usuario_encargado == User.id_usuario)\
     .outerjoin(Moneda, OrdenServicio.id_moneda == Moneda.id_moneda)\
     .outerjoin(Bodega, OrdenServicio.id_bodega == Bodega.id_bodega)\
     .outerjoin(Empresa, OrdenServicio.id_empresa == Empresa.id_empresa)\
     .outerjoin(EstadoOrdenServicio, OrdenServicio.id_estado_orden_servicio == EstadoOrdenServicio.id_estado_orden_servicio)

    if id_orden_servicio is not None:
        base_query = base_query.filter(OrdenServicio.id_orden_servicio == id_orden_servicio)
    if proveedor is not None:
        base_query = base_query.filter(ClienteProveedor.razon_social.ilike(f"%{proveedor}%"))
    if usuario_encargado is not None:
        base_query = base_query.filter(User.nombre.ilike(f"%{usuario_encargado}%"))

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
            "bodega_nombre": row.bodega_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
        })
        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


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

    proveedor = getattr(item, "ClienteProveedor", None)
    usuario = getattr(item, "UsuarioEncargado", None)
    moneda = getattr(item, "Moneda", None)
    bodega = getattr(item, "Bodega", None)
    empresa = getattr(item, "Empresa", None)
    estado = getattr(item, "EstadoOrdenServicio", None)

    os_dict["proveedor_nombre"] = getattr(proveedor, "razon_social", None)
    os_dict["usuario_nombre"] = getattr(usuario, "nombre", None)
    os_dict["moneda_nombre"] = getattr(moneda, "etiqueta", None)
    os_dict["bodega_nombre"] = getattr(bodega, "nombre", None)
    os_dict["empresa_nombre"] = getattr(empresa, "nombre_fantasia", None)
    os_dict["estado_nombre"] = getattr(estado, "nombre", None)

    detalles_servicio = []
    if hasattr(item, 'DetalleOrdenServicio') and item.DetalleOrdenServicio is not None:
        detalles_query = item.DetalleOrdenServicio
        detalles_list = detalles_query.all() if hasattr(detalles_query, 'all') else detalles_query
        for d in detalles_list:
            if hasattr(d, 'to_dict'):
                detalles_servicio.append(d.to_dict())
            else:
                detalles_servicio.append(dict(d.__dict__))
    os_dict["detalles_orden_servicio"] = detalles_servicio

    return os_dict


@router.put("/{item_id}", response_model=OrdenServicioRead)
def update_orden_servicio(item_id: int, payload: OrdenServicioUpdate, db: Session = Depends(get_db)):
    item = db.get(OrdenServicio, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenServicio not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
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
