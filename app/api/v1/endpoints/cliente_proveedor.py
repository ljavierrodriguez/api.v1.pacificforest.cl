from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.cliente_proveedor import ClienteProveedor
from app.schemas.cliente_proveedor import (
    ClienteProveedorCreate,
    ClienteProveedorRead,
    ClienteProveedorUpdate,
)

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


@router.get("/", response_model=List[ClienteProveedorRead], summary='GET Cliente Proveedor', description='GET Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def list_cliente_proveedor(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(ClienteProveedor).offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=ClienteProveedorRead, summary='GET Cliente Proveedor', description='GET Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def get_cliente_proveedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")
    return item


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


@router.delete("/{item_id}", summary='DELETE Cliente Proveedor', description='DELETE Cliente Proveedor endpoint. Replace this placeholder with a meaningful description.')
def delete_cliente_proveedor(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ClienteProveedor, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ClienteProveedor not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
