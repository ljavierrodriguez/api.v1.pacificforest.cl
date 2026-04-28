from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from decimal import Decimal, InvalidOperation
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.detalle_proforma import DetalleProforma
from app.models.orden_compra import OrdenCompra
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


@router.post("/", response_model=OrdenCompraRead, status_code=201, summary='POST OrdenCompra', description='Crear una nueva orden de compra.')
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

    # Validar productos y volumen contra la proforma, incluso para OCs clonadas.
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
        ).filter(
            OrdenCompra.id_proforma == payload.id_proforma,
        ).scalar()

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


from app.models.proforma import Proforma
from app.models.operacion_exportacion import OperacionExportacion

# ... (omitting other imports)

@router.get("/", response_model=PaginatedOrdenCompraResponse, summary='GET OrdenCompra', description='Obtener lista de órdenes de compra con paginación.')
def list_orden_compra(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
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
        OperacionExportacion.id_operacion_exportacion.label("oe_numero")
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
            "volumenTotal": row.volumenTotal,
            "proveedor_nombre": row.proveedor_nombre,
            "usuario_nombre": row.usuario_nombre,
            "moneda_nombre": row.moneda_nombre,
            "bodega_nombre": row.bodega_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
            "oe_numero": str(row.oe_numero) if row.oe_numero else None
        })
        items.append(item_dict)
    
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/search", response_model=PaginatedOrdenCompraResponse, summary='Buscar Órdenes de Compra', description='Buscar órdenes de compra por N° OC, N° proforma, N° OE, proveedor o usuario encargado.')
def search_orden_compra(
    id_orden_compra: Optional[int] = Query(None, description="Filtrar por N° de orden de compra"),
    id_proforma: Optional[int] = Query(None, description="Filtrar por N° de proforma"),
    id_operacion_exportacion: Optional[int] = Query(None, description="Filtrar por N° de operación de exportación"),
    proveedor: Optional[str] = Query(None, description="Buscar por razón social del proveedor (búsqueda parcial)"),
    usuario_encargado: Optional[str] = Query(None, description="Buscar por nombre del usuario encargado (búsqueda parcial)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size

    # Subconsulta para volumen total por OC
    volumen_sub = db.query(
        DetalleOrdenCompra.id_orden_compra,
        func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, 0)).label("vol_total")
    ).group_by(DetalleOrdenCompra.id_orden_compra).subquery()

    # Consulta base con todos los joins
    base_query = db.query(
        OrdenCompra,
        func.coalesce(volumen_sub.c.vol_total, 0).label("volumenTotal"),
        ClienteProveedor.razon_social.label("proveedor_nombre"),
        User.nombre.label("usuario_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        Bodega.nombre.label("bodega_nombre"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        EstadoOdc.nombre.label("estado_nombre"),
        OperacionExportacion.id_operacion_exportacion.label("oe_numero")
    ).outerjoin(volumen_sub, OrdenCompra.id_orden_compra == volumen_sub.c.id_orden_compra)\
     .outerjoin(ClienteProveedor, OrdenCompra.id_cliente_proveedor == ClienteProveedor.id_cliente_proveedor)\
     .outerjoin(User, OrdenCompra.id_usuario_encargado == User.id_usuario)\
     .outerjoin(Moneda, OrdenCompra.id_moneda == Moneda.id_moneda)\
     .outerjoin(Bodega, OrdenCompra.id_bodega == Bodega.id_bodega)\
     .outerjoin(Empresa, OrdenCompra.id_empresa == Empresa.id_empresa)\
     .outerjoin(EstadoOdc, OrdenCompra.id_estado_odc == EstadoOdc.id_estado_odc)\
     .outerjoin(Proforma, OrdenCompra.id_proforma == Proforma.id_proforma)\
     .outerjoin(OperacionExportacion, Proforma.id_operacion_exportacion == OperacionExportacion.id_operacion_exportacion)

    # Aplicar filtros
    if id_orden_compra is not None:
        base_query = base_query.filter(OrdenCompra.id_orden_compra == id_orden_compra)
    if id_proforma is not None:
        base_query = base_query.filter(OrdenCompra.id_proforma == id_proforma)
    if id_operacion_exportacion is not None:
        base_query = base_query.filter(OperacionExportacion.id_operacion_exportacion == id_operacion_exportacion)
    if proveedor is not None:
        base_query = base_query.filter(ClienteProveedor.razon_social.ilike(f"%{proveedor}%"))
    if usuario_encargado is not None:
        base_query = base_query.filter(User.nombre.ilike(f"%{usuario_encargado}%"))

    total_items = base_query.count()

    results = base_query.order_by(desc(OrdenCompra.id_orden_compra))\
                        .offset(skip).limit(page_size).all()

    items = []
    for row in results:
        oc = row[0]
        item_dict = oc.__dict__.copy()
        item_dict.update({
            "volumenTotal": row.volumenTotal,
            "proveedor_nombre": row.proveedor_nombre,
            "usuario_nombre": row.usuario_nombre,
            "moneda_nombre": row.moneda_nombre,
            "bodega_nombre": row.bodega_nombre,
            "empresa_nombre": row.empresa_nombre,
            "estado_nombre": row.estado_nombre,
            "oe_numero": str(row.oe_numero) if row.oe_numero else None,
        })
        items.append(item_dict)

    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=OrdenCompraRead, summary='GET OrdenCompra', description='Obtener una orden de compra específica por ID.')
def get_orden_compra(item_id: int, db: Session = Depends(get_db)):
    item = db.get(OrdenCompra, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrdenCompra not found")
    return item


@router.put("/{item_id}", response_model=OrdenCompraRead, summary='PUT OrdenCompra', description='Actualizar una orden de compra existente.')
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


@router.delete("/{item_id}", summary='DELETE OrdenCompra', description='Eliminar una orden de compra.')
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