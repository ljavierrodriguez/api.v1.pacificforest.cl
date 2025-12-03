from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.plc import Plc
from app.schemas.plc import PlcCreate, PlcRead, PlcUpdate

router = APIRouter(prefix="/plc", tags=["plc"])


@router.post("/", response_model=PlcRead, summary='POST Plc', description='POST Plc endpoint. Replace this placeholder with a meaningful description.')
def create_plc(payload: PlcCreate, db: Session = Depends(get_db)):
    obj = Plc(
        id_operacion_exportacion=payload.id_operacion_exportacion,
        id_estado_pl=payload.id_estado_pl,
        fecha_creacion=payload.fecha_creacion,
        volumen_m3=payload.volumen_m3,
        paquetes=payload.paquetes,
        peso_bruto=payload.peso_bruto,
        piezas=payload.piezas,
        descripcion=payload.descripcion,
        categoria_fsc=payload.categoria_fsc,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[PlcRead], summary='GET Plc', description='GET Plc endpoint. Replace this placeholder with a meaningful description.')
def list_plc(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Plc).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=PlcRead, summary='GET Plc', description='GET Plc endpoint. Replace this placeholder with a meaningful description.')
def get_plc(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Plc, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Plc not found")
    return item


@router.put("/{item_id}", response_model=PlcRead, summary='PUT Plc', description='PUT Plc endpoint. Replace this placeholder with a meaningful description.')
def update_plc(item_id: int, payload: PlcUpdate, db: Session = Depends(get_db)):
    item = db.get(Plc, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Plc not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Plc', description='DELETE Plc endpoint. Replace this placeholder with a meaningful description.')
def delete_plc(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Plc, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Plc not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
