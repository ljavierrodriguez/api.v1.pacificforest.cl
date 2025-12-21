from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.orden_compra import OrdenCompra
from app.schemas.orden_compra import OrdenCompraCreate, OrdenCompraRead, OrdenCompraUpdate

router = APIRouter(prefix="/orden_compra", tags=["orden_compra"])


@router.post("/", response_model=OrdenCompraRead, status_code=201, summary='POST OrdenCompra', description='Crear una nueva orden de compra.')
def create_orden_compra(payload: OrdenCompraCreate, db: Session = Depends(get_db)):
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
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[OrdenCompraRead], summary='GET OrdenCompra', description='Obtener lista de órdenes de compra con paginación.')
def list_orden_compra(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(OrdenCompra).offset(skip).limit(limit).all()


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
        db.delete(item)
        db.commit()
        return {"ok": True}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))