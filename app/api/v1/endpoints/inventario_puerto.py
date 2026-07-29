from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional, List
from datetime import date

from app.db.session import get_db
from app.models.inventario_puerto import InventarioPuerto
from app.models.orden_servicio import OrdenServicio
from app.models.detalle_orden_servicio import DetalleOrdenServicio
from app.schemas.inventario_puerto import (
    InventarioPuertoCreate,
    InventarioPuertoUpdate,
    InventarioPuertoRead,
    PaginatedInventarioPuertoResponse,
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
    id_producto: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    id_bodega: Optional[int] = Query(None, description="Filtrar por ID de bodega"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
):
    query = db.query(InventarioPuerto)

    if id_orden_servicio:
        query = query.filter(InventarioPuerto.id_orden_servicio == id_orden_servicio)
    if id_producto:
        query = query.filter(InventarioPuerto.id_producto == id_producto)
    if id_bodega:
        query = query.filter(InventarioPuerto.id_bodega == id_bodega)
    if estado:
        query = query.filter(InventarioPuerto.estado.ilike(f"%{estado}%"))

    if search and search.strip():
        s = search.strip()
        if s.isdigit():
            query = query.filter(
                or_(
                    InventarioPuerto.id_inventario_puerto == int(s),
                    InventarioPuerto.id_orden_servicio == int(s),
                )
            )
        else:
            query = query.filter(
                or_(
                    InventarioPuerto.texto_abierto.ilike(f"%{s}%"),
                    InventarioPuerto.observaciones.ilike(f"%{s}%"),
                    InventarioPuerto.estado.ilike(f"%{s}%"),
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

    bodega_id = payload and payload.id_bodega
    fecha_rec = (payload and payload.fecha_recepcion) or date.today()
    obs_general = (payload and payload.observaciones) or None

    items_map = {}
    if payload and payload.items:
        for item in payload.items:
            if item.id_detalle_os:
                items_map[item.id_detalle_os] = item

    created_items = []
    for d in detalles:
        item_override = items_map.get(d.id_detalle_os)
        cant = item_override.cantidad if (item_override and item_override.cantidad is not None) else d.cantidad
        pzs = item_override.piezas if (item_override and item_override.piezas is not None) else None
        vol = item_override.volumen if (item_override and item_override.volumen is not None) else d.volumen
        vol_eq = item_override.volumen_eq if (item_override and item_override.volumen_eq is not None) else d.volumen_eq
        bodega_item = item_override.id_bodega if (item_override and item_override.id_bodega) else bodega_id
        obs = item_override.observaciones if (item_override and item_override.observaciones) else obs_general

        inv = InventarioPuerto(
            id_orden_servicio=os_obj.id_orden_servicio,
            id_detalle_os=d.id_detalle_os,
            id_producto=d.id_producto,
            id_bodega=bodega_item,
            id_unidad_venta=d.id_unidad_venta,
            texto_abierto=d.texto_abierto,
            espesor=d.espesor,
            id_unidad_medida_espesor=d.id_unidad_medida_espesor,
            ancho=d.ancho,
            id_unidad_medida_ancho=d.id_unidad_medida_ancho,
            largo=d.largo,
            id_unidad_medida_largo=d.id_unidad_medida_largo,
            cantidad=cant,
            precio_unitario=d.precio_unitario,
            subtotal=d.subtotal,
            volumen=vol,
            volumen_eq=vol_eq,
            precio_eq=d.precio_eq,
            piezas=pzs,
            fecha_recepcion=fecha_rec,
            observaciones=obs,
            estado="RECIBIDO",
        )
        db.add(inv)
        created_items.append(inv)

    db.commit()

    for item in created_items:
        db.refresh(item)

    return [InventarioPuertoRead(**item.to_dict()) for item in created_items]


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
