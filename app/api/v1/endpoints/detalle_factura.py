from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.detalle_factura import DetalleFactura
from app.schemas.detalle_factura import (
    DetalleFacturaCreate,
    DetalleFacturaRead,
    DetalleFacturaUpdate,
)

router = APIRouter(prefix="/detalle_factura", tags=["detalle_factura"])


@router.post("/", response_model=DetalleFacturaRead, summary='POST Detalle Factura', description='POST Detalle Factura endpoint. Replace this placeholder with a meaningful description.')
def create_detalle(payload: DetalleFacturaCreate, db: Session = Depends(get_db)):
    obj = DetalleFactura(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[DetalleFacturaRead], summary='GET Detalle Factura', description='GET Detalle Factura endpoint. Replace this placeholder with a meaningful description.')
def list_detalles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DetalleFactura).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=DetalleFacturaRead, summary='GET Detalle Factura', description='GET Detalle Factura endpoint. Replace this placeholder with a meaningful description.')
def get_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleFactura, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@router.put("/{item_id}", response_model=DetalleFacturaRead, summary='PUT Detalle Factura', description='PUT Detalle Factura endpoint. Replace this placeholder with a meaningful description.')
def update_detalle(item_id: int, payload: DetalleFacturaUpdate, db: Session = Depends(get_db)):
    item = db.get(DetalleFactura, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Detalle Factura', description='DELETE Detalle Factura endpoint. Replace this placeholder with a meaningful description.')
def delete_detalle(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DetalleFactura, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
