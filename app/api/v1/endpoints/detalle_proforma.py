from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.db.session import get_db
from app.models.detalle_proforma import DetalleProforma
from app.schemas.detalle_proforma import (
    DetalleProformaCreate,
    DetalleProformaRead,
    DetalleProformaUpdate,
    ProductoBasico,
)
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para DetalleProforma
PaginatedDetalleProformaResponse = create_paginated_response_model(DetalleProformaRead)

router = APIRouter(prefix="/detalle_proforma", tags=["detalle_proforma"])


def _build_detalle_response(detalle: DetalleProforma) -> dict:
    """Helper function to build response with producto data"""
    response_data = {
        "id_detalle_proforma": detalle.id_detalle_proforma,
        "id_proforma": detalle.id_proforma,
        "id_producto": detalle.id_producto,
        "id_unidad_venta": detalle.id_unidad_venta,
        "texto_libre": detalle.texto_libre,
        "espesor": detalle.espesor,
        "id_unidad_medida_espesor": detalle.id_unidad_medida_espesor,
        "ancho": detalle.ancho,
        "id_unidad_medida_ancho": detalle.id_unidad_medida_ancho,
        "largo": detalle.largo,
        "id_unidad_medida_largo": detalle.id_unidad_medida_largo,
        "piezas": detalle.piezas,
        "cantidad": detalle.cantidad,
        "precio_unitario": detalle.precio_unitario,
        "subtotal": detalle.subtotal,
        "volumen": detalle.volumen,
        "volumen_eq": detalle.volumen_eq,
        "precio_eq": detalle.precio_eq,
    }
    
    # Agregar datos del producto si existe
    if detalle.Producto is not None:
        response_data["producto"] = {
            "id_producto": detalle.Producto.id_producto,
            "nombre_producto_esp": detalle.Producto.nombre_producto_esp,
            "nombre_producto_ing": detalle.Producto.nombre_producto_ing,
            "obs_calidad": detalle.Producto.obs_calidad,
        }
    else:
        response_data["producto"] = None
    
    return response_data


@router.post("/", status_code=201, summary='POST Detalle Proforma', description='Crear un nuevo detalle de proforma.')
def create_detalle_proforma(payload: DetalleProformaCreate, db: Session = Depends(get_db)):
    obj = DetalleProforma(
        id_proforma=payload.id_proforma,
        id_producto=payload.id_producto,
        id_unidad_venta=payload.id_unidad_venta,
        texto_libre=payload.texto_libre,
        espesor=payload.espesor,
        id_unidad_medida_espesor=payload.id_unidad_medida_espesor,
        ancho=payload.ancho,
        id_unidad_medida_ancho=payload.id_unidad_medida_ancho,
        largo=payload.largo,
        id_unidad_medida_largo=payload.id_unidad_medida_largo,
        piezas=payload.piezas,
        cantidad=payload.cantidad,
        precio_unitario=payload.precio_unitario,
        subtotal=payload.subtotal,
        volumen=payload.volumen,
        volumen_eq=payload.volumen_eq,
        precio_eq=payload.precio_eq,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    
    # Cargar el producto si existe
    if obj.id_producto:
        obj = db.query(DetalleProforma).options(joinedload(DetalleProforma.Producto)).filter(
            DetalleProforma.id_detalle_proforma == obj.id_detalle_proforma
        ).first()
    
    return _build_detalle_response(obj)


@router.get("/", response_model=PaginatedDetalleProformaResponse, summary='GET Detalle Proforma', description='Obtener lista de detalles de proforma con paginación.')
def list_detalle_proforma(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    # Obtener total de elementos
    total_items = db.query(DetalleProforma).count()
    
    # Obtener elementos de la página actual con datos del producto
    items = (db.query(DetalleProforma)
             .options(joinedload(DetalleProforma.Producto))
             .offset(skip)
             .limit(page_size)
             .all())
    
    # Construir respuesta con datos del producto
    items_with_producto = [_build_detalle_response(item) for item in items]
    
    # Crear respuesta paginada
    return create_paginated_response(items_with_producto, page, page_size, total_items)


@router.get("/by-proforma/{id_proforma}", response_model=List[DetalleProformaRead], summary='GET Detalles por Proforma', description='Obtener todos los detalles de una proforma específica.')
def get_detalles_by_proforma(id_proforma: int, db: Session = Depends(get_db)):
    # Cargar todos los detalles de la proforma con los datos del producto
    items = (db.query(DetalleProforma)
             .options(joinedload(DetalleProforma.Producto))
             .filter(DetalleProforma.id_proforma == id_proforma)
             .all())
    
    # Construir respuesta con datos del producto
    return [_build_detalle_response(item) for item in items]


@router.get("/{item_id}", response_model=DetalleProformaRead, summary='GET Detalle Proforma', description='Obtener un detalle de proforma específico por ID.')
def get_detalle_proforma(item_id: int, db: Session = Depends(get_db)):
    # Cargar el detalle con los datos del producto
    item = (db.query(DetalleProforma)
            .options(joinedload(DetalleProforma.Producto))
            .filter(DetalleProforma.id_detalle_proforma == item_id)
            .first())
    
    if not item:
        raise HTTPException(status_code=404, detail="DetalleProforma not found")
    
    return _build_detalle_response(item)


@router.put("/{item_id}", summary='PUT Detalle Proforma', description='Actualizar un detalle de proforma existente.')
def update_detalle_proforma(item_id: int, payload: DetalleProformaUpdate, db: Session = Depends(get_db)):
    item = db.get(DetalleProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DetalleProforma not found")
    
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Cargar el producto actualizado si existe
    if item.id_producto:
        item = (db.query(DetalleProforma)
                .options(joinedload(DetalleProforma.Producto))
                .filter(DetalleProforma.id_detalle_proforma == item_id)
                .first())
    
    return _build_detalle_response(item)


@router.delete("/{item_id}", summary='DELETE Detalle Proforma', description='Eliminar un detalle de proforma.')
def delete_detalle_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleProforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DetalleProforma not found")
    
    db.delete(item)
    db.commit()
    return {"ok": True}
