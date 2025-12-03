from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.proforma import Proforma
from app.schemas.proforma import ProformaCreate, ProformaRead, ProformaUpdate

router = APIRouter(prefix="/proforma", tags=["proforma"])


@router.post("/", response_model=ProformaRead, summary='POST Proforma', description='POST Proforma endpoint. Replace this placeholder with a meaningful description.')
def create_proforma(payload: ProformaCreate, db: Session = Depends(get_db)):
    obj = Proforma(
        id_cliente_proveedor=payload.id_cliente_proveedor,
        fecha=payload.fecha,
        total=payload.total,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[ProformaRead], summary='GET Proforma', description='GET Proforma endpoint. Replace this placeholder with a meaningful description.')
def list_proforma(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Proforma).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=ProformaRead, summary='GET Proforma', description='GET Proforma endpoint. Replace this placeholder with a meaningful description.')
def get_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    return item


@router.put("/{item_id}", response_model=ProformaRead, summary='PUT Proforma', description='PUT Proforma endpoint. Replace this placeholder with a meaningful description.')
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


@router.delete("/{item_id}", summary='DELETE Proforma', description='DELETE Proforma endpoint. Replace this placeholder with a meaningful description.')
def delete_proforma(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Proforma, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Proforma not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
