from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.db.session import get_db
from app.models.ciudad import Ciudad
from app.models.cliente_proveedor import ClienteProveedor
from app.models.contacto import Contacto
from app.models.direccion import Direccion
from app.schemas.cliente_proveedor import (
    ClienteProveedorCreate,
    ClienteProveedorDetailRead,
    ClienteProveedorRead,
    ClienteProveedorUpdate,
)
from app.schemas.pagination import create_paginated_response, create_paginated_response_model

# Crear el modelo de respuesta paginada para ClienteProveedor
PaginatedClienteProveedorResponse = create_paginated_response_model(ClienteProveedorRead)

router = APIRouter(prefix="/cliente_proveedor", tags=["cliente_proveedor"])


@router.post("/", response_model=ClienteProveedorRead, summary='POST Cliente Proveedor', description='POST Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def create_cliente_proveedor(
    payload: ClienteProveedorCreate, db: Session = Depends(get_db)
):
    obj = ClienteProveedor(
        rut=payload.rut,
        nombre_fantasia=payload.nombre_fantasia,
        razon_social=payload.razon_social,
        es_nacional=payload.es_nacional,
        giro=payload.giro,
        es_cliente=payload.es_cliente,
        es_proveedor=payload.es_proveedor,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=PaginatedClienteProveedorResponse, summary='GET Cliente Proveedor', description='Obtener lista de clientes/proveedores con paginación.')
def list_cliente_proveedor(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    es_proveedor: Optional[bool] = Query(None, description="Filtrar por proveedores"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size
    
    base_query = db.query(ClienteProveedor)
    if es_proveedor is not None:
        base_query = base_query.filter(ClienteProveedor.es_proveedor == es_proveedor)

    # Obtener total de elementos
    total_items = base_query.count()
    
    # Obtener elementos de la página actual ordenados alfabéticamente
    items = (
        base_query
        .order_by(ClienteProveedor.razon_social.asc(), ClienteProveedor.nombre_fantasia.asc())
        .offset(skip)
        .limit(page_size)
        .all()
    )
    
    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/search", response_model=PaginatedClienteProveedorResponse, summary='SEARCH Cliente Proveedor', description='Buscar clientes/proveedores por texto con paginación.')
def search_cliente_proveedor(
    q: str = Query(..., min_length=1, description="Texto a buscar en RUT, nombre fantasía, razón social o giro"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    es_proveedor: Optional[bool] = Query(None, description="Filtrar por proveedores"),
    db: Session = Depends(get_db)
):
    # Calcular offset
    skip = (page - 1) * page_size

    search = f"%{q.strip()}%"
    query = db.query(ClienteProveedor).filter(
        or_(
            ClienteProveedor.rut.ilike(search),
            ClienteProveedor.nombre_fantasia.ilike(search),
            ClienteProveedor.razon_social.ilike(search),
            ClienteProveedor.giro.ilike(search),
        )
    )

    if es_proveedor is not None:
        query = query.filter(ClienteProveedor.es_proveedor == es_proveedor)

    # Obtener total de elementos filtrados
    total_items = query.count()

    # Obtener elementos de la página actual ordenados alfabéticamente
    items = (
        query
        .order_by(ClienteProveedor.razon_social.asc(), ClienteProveedor.nombre_fantasia.asc())
        .offset(skip)
        .limit(page_size)
        .all()
    )

    # Crear respuesta paginada
    return create_paginated_response(items, page, page_size, total_items)


@router.get("/{item_id}", response_model=ClienteProveedorDetailRead, summary='GET Cliente Proveedor', description='GET Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def get_cliente_proveedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")

    contactos = (
        db.query(Contacto)
        .filter(Contacto.id_cliente_proveedor == item_id)
        .order_by(Contacto.nombre.asc())
        .all()
    )
    direcciones = (
        db.query(Direccion)
        .options(joinedload(Direccion.Ciudad).joinedload(Ciudad.Pais))
        .filter(Direccion.id_cliente_proveedor == item_id)
        .order_by(Direccion.por_defecto.desc(), Direccion.direccion.asc())
        .all()
    )

    return {
        **ClienteProveedorRead.model_validate(item).model_dump(),
        "Contactos": contactos,
        "Direcciones": direcciones,
    }


@router.put("/{item_id}", response_model=ClienteProveedorRead, summary='PUT Cliente Proveedor', description='PUT Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def update_cliente_proveedor(
    item_id: int, payload: ClienteProveedorUpdate, db: Session = Depends(get_db)
):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Cliente Proveedor', description='Eliminar un cliente/proveedor.')
def delete_cliente_proveedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")
    
    # Verificar relaciones asociadas
    contactos_count = item.Contactos.count()
    direcciones_count = item.Direcciones.count()
    ordenes_count = item.OrdenesCompra.count()
    operaciones_facturar = item.OperacionesFacturar.count()
    operaciones_consignar = item.OperacionesConsignar.count()
    operaciones_notificar = item.OperacionesNotificar.count()
    
    total_relaciones = (contactos_count + direcciones_count + ordenes_count + 
                       operaciones_facturar + operaciones_consignar + operaciones_notificar)
    
    if total_relaciones > 0:
        detalles = []
        if contactos_count > 0:
            detalles.append(f"{contactos_count} contacto(s)")
        if direcciones_count > 0:
            detalles.append(f"{direcciones_count} dirección(es)")
        if ordenes_count > 0:
            detalles.append(f"{ordenes_count} orden(es) de compra")
        if operaciones_facturar > 0:
            detalles.append(f"{operaciones_facturar} operación(es) de facturación")
        if operaciones_consignar > 0:
            detalles.append(f"{operaciones_consignar} operación(es) de consignación")
        if operaciones_notificar > 0:
            detalles.append(f"{operaciones_notificar} operación(es) de notificación")
        
        mensaje = f"No se puede eliminar el cliente/proveedor porque tiene: {', '.join(detalles)}"
        raise HTTPException(status_code=400, detail=mensaje)
    
    db.delete(item)
    db.commit()
    return {"ok": True}
