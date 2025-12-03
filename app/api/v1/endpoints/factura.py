from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.factura import Factura
from app.schemas.factura import FacturaCreate, FacturaRead, FacturaUpdate
from app.db.session import get_db

router = APIRouter(prefix="/facturas", tags=["facturas"])


@router.post("/", response_model=FacturaRead, status_code=201, summary='POST Factura', description='POST Factura endpoint. Replace this placeholder with a meaningful description.')
def create_factura(payload: FacturaCreate, db: Session = Depends(get_db)):
    obj = Factura(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[FacturaRead], summary='GET Factura', description='GET Factura endpoint. Replace this placeholder with a meaningful description.')
def list_facturas(db: Session = Depends(get_db)):
    return db.query(Factura).all()


@router.get("/{item_id}", response_model=FacturaRead, summary='GET Factura', description='GET Factura endpoint. Replace this placeholder with a meaningful description.')
def get_factura(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Factura, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return obj


@router.put("/{item_id}", response_model=FacturaRead, summary='PUT Factura', description='PUT Factura endpoint. Replace this placeholder with a meaningful description.')
def update_factura(item_id: int, payload: FacturaUpdate, db: Session = Depends(get_db)):
    obj = db.get(Factura, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=204, summary='DELETE Factura', description='DELETE Factura endpoint. Replace this placeholder with a meaningful description.')
def delete_factura(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Factura, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    db.delete(obj)
    db.commit()
    return
