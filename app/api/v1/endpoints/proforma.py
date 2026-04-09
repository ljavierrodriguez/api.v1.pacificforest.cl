from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session, aliased
from sqlalchemy import desc, func, select, literal_column, cast, Numeric
from typing import List
from io import BytesIO
import os
import shutil
from datetime import datetime
from app.db.session import get_db
from app.models.proforma import Proforma
from app.models.detalle_proforma import DetalleProforma
from app.models.orden_compra import OrdenCompra
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.empresa import Empresa
from app.models.moneda import Moneda
from app.models.estado_proforma import EstadoProforma
from app.models.usuario import User
from app.models.direccion import Direccion
from app.models.cliente_proveedor import ClienteProveedor
from app.models.operacion_exportacion import OperacionExportacion
from app.schemas.proforma import ProformaCreate, ProformaRead, ProformaUpdate
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
    return obj


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
    
    # Subconsulta para volumen total de proforma (cast de String a Numeric, manejando comas)
    volumen_total_sub = db.query(
        DetalleProforma.id_proforma,
        func.sum(cast(func.coalesce(func.replace(DetalleProforma.volumen_eq, ',', '.'), '0'), Numeric(12, 3))).label("vol_total")
    ).group_by(DetalleProforma.id_proforma).subquery()

    # Subconsulta para volumen total por OC (Numeric(12, 3) ya es numérico)
    volumen_per_oc_sub = db.query(
        DetalleOrdenCompra.id_orden_compra,
        func.sum(func.coalesce(DetalleOrdenCompra.volumen_eq, 0)).label("vol_oc")
    ).group_by(DetalleOrdenCompra.id_orden_compra).subquery()

    # Subconsulta para volumen asignado y conteo de OCs por Proforma
    oc_summary_sub = db.query(
        OrdenCompra.id_proforma,
        func.count(OrdenCompra.id_orden_compra).label("cnt_oc"),
        func.sum(func.coalesce(volumen_per_oc_sub.c.vol_oc, 0)).label("vol_asig")
    ).outerjoin(volumen_per_oc_sub, OrdenCompra.id_orden_compra == volumen_per_oc_sub.c.id_orden_compra)\
     .group_by(OrdenCompra.id_proforma).subquery()

    # Alias para joins de direcciones (facturar)
    DirFacturar = aliased(Direccion)
    CPFacturar = aliased(ClienteProveedor)

    # Consulta principal con joins para etiquetas
    query = db.query(
        Proforma,
        func.coalesce(volumen_total_sub.c.vol_total, 0).label("volumenTotal"),
        func.coalesce(oc_summary_sub.c.vol_asig, 0).label("volumenAsignado"),
        func.coalesce(oc_summary_sub.c.cnt_oc, 0).label("oc_asociadas"),
        Empresa.nombre_fantasia.label("empresa_nombre"),
        Moneda.etiqueta.label("moneda_nombre"),
        EstadoProforma.nombre.label("estado_nombre"),
        User.nombre.label("usuario_nombre"),
        CPFacturar.razon_social.label("facturar_a_nombre"),
        OperacionExportacion.numero_operacion.label("oe_numero")
    ).outerjoin(volumen_total_sub, Proforma.id_proforma == volumen_total_sub.c.id_proforma)\
     .outerjoin(oc_summary_sub, Proforma.id_proforma == oc_summary_sub.c.id_proforma)\
     .outerjoin(Empresa, Proforma.id_empresa == Empresa.id_empresa)\
     .outerjoin(Moneda, Proforma.id_moneda == Moneda.id_moneda)\
     .outerjoin(EstadoProforma, Proforma.id_estado_proforma == EstadoProforma.id_estado_proforma)\
     .outerjoin(User, Proforma.id_usuario_encargado == User.id_usuario)\
     .outerjoin(OperacionExportacion, Proforma.id_operacion_exportacion == OperacionExportacion.id_operacion_exportacion)\
     .outerjoin(DirFacturar, Proforma.id_direccion_facturar == DirFacturar.id_direccion)\
     .outerjoin(CPFacturar, DirFacturar.id_cliente_proveedor == CPFacturar.id_cliente_proveedor)\
     .order_by(desc(Proforma.fecha_emision), desc(Proforma.id_proforma))\
     .offset(skip).limit(page_size)

    results = query.all()
    
    items = []
    for row in results:
        proforma = row[0]
        vol_total = float(row[1] or 0)
        vol_asig = float(row[2] or 0)
        oc_cnt = int(row[3] or 0)
        
        # Calcular campos adicionales
        vol_pend = max(vol_total - vol_asig, 0)
        
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
            "volumenAsignado": vol_asig,
            "volumenPendiente": vol_pend,
            "oc_asociadas": oc_cnt,
            "estadoFlujo": estado_flujo,
            "empresa_nombre": row.empresa_nombre,
            "moneda_nombre": row.moneda_nombre,
            "estado_nombre": row.estado_nombre,
            "usuario_nombre": row.usuario_nombre,
            "facturar_a_nombre": row.facturar_a_nombre,
            "oe_numero": row.oe_numero
        })
        items.append(item_dict)
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ProformaRead, summary='GET Proforma', description='Obtener una proforma específica por ID.')
def get_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    return item


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
    return item


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
            headers={"Content-Disposition": f"attachment; filename=Proforma_{item_id}_ES.pdf"}
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
            headers={"Content-Disposition": f"attachment; filename=Proforma_{item_id}_EN.pdf"}
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
            headers={"Content-Disposition": f"attachment; filename=Proforma_{item_id}_{lang_suffix}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
