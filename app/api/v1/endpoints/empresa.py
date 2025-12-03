from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaCreate, EmpresaRead, EmpresaUpdate

router = APIRouter(prefix="/empresa", tags=["empresa"])


@router.post("/", response_model=EmpresaRead, summary='POST Empresa', description='POST Empresa endpoint. Replace this placeholder with a meaningful description.')
def create_empresa(payload: EmpresaCreate, db: Session = Depends(get_db)):
    obj = Empresa(
        rut=payload.rut,
        razon_social=payload.razon_social,
        nombre_fantasia=payload.nombre_fantasia,
        correo=str(payload.correo) if payload.correo else None,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[EmpresaRead], summary='GET Empresa', description='GET Empresa endpoint. Replace this placeholder with a meaningful description.')
def list_empresa(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Empresa).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=EmpresaRead, summary='GET Empresa', description='GET Empresa endpoint. Replace this placeholder with a meaningful description.')
def get_empresa(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    return item


@router.put("/{item_id}", response_model=EmpresaRead, summary='PUT Empresa', description='PUT Empresa endpoint. Replace this placeholder with a meaningful description.')
def update_empresa(item_id: int, payload: EmpresaUpdate, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Empresa', description='DELETE Empresa endpoint. Replace this placeholder with a meaningful description.')
def delete_empresa(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Empresa, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Empresa not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
