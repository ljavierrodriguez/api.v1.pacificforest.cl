from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.ple import Ple
from app.schemas.ple import PleCreate, PleRead, PleUpdate

router = APIRouter(prefix="/ple", tags=["ple"])


@router.post("/", response_model=PleRead, summary='POST Ple', description='POST Ple endpoint. Replace this placeholder with a meaningful description.')
def create_ple(payload: PleCreate, db: Session = Depends(get_db)):
    obj = Ple(id_estado_pl=payload.id_estado_pl, fecha=payload.fecha)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[PleRead], summary='GET Ple', description='GET Ple endpoint. Replace this placeholder with a meaningful description.')
def list_ple(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Ple).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=PleRead, summary='GET Ple', description='GET Ple endpoint. Replace this placeholder with a meaningful description.')
def get_ple(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ple, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ple not found")
    return item


@router.put("/{item_id}", response_model=PleRead, summary='PUT Ple', description='PUT Ple endpoint. Replace this placeholder with a meaningful description.')
def update_ple(item_id: int, payload: PleUpdate, db: Session = Depends(get_db)):
    item = db.get(Ple, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ple not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Ple', description='DELETE Ple endpoint. Replace this placeholder with a meaningful description.')
def delete_ple(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ple, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ple not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
