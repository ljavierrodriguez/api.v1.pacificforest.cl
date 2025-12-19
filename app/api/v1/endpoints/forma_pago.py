from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.forma_pago import FormaPago
from app.schemas.forma_pago import FormaPagoCreate, FormaPagoRead, FormaPagoUpdate

router = APIRouter(prefix="/forma_pago", tags=["forma_pago"])


@router.post("/", response_model=FormaPagoRead, status_code=201, summary='POST FormaPago', description='Crear una nueva forma de pago.')
def create_forma_pago(payload: FormaPagoCreate, db: Session = Depends(get_db)):
    obj = FormaPago(
        nombre=payload.nombre,
        por_defecto=payload.por_defecto,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[FormaPagoRead], summary='GET FormaPago', description='Obtener lista de formas de pago con paginación.')
def list_forma_pago(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(FormaPago).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=FormaPagoRead, summary='GET FormaPago', description='Obtener una forma de pago específica por ID.')
def get_forma_pago(item_id: int, db: Session = Depends(get_db)):
    item = db.get(FormaPago, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="FormaPago not found")
    return item


@router.put("/{item_id}", response_model=FormaPagoRead, summary='PUT FormaPago', description='Actualizar una forma de pago existente.')
def update_forma_pago(item_id: int, payload: FormaPagoUpdate, db: Session = Depends(get_db)):
    item = db.get(FormaPago, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="FormaPago not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE FormaPago', description='Eliminar una forma de pago.')
def delete_forma_pago(item_id: int, db: Session = Depends(get_db)):
    item = db.get(FormaPago, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="FormaPago not found")
    db.delete(item)
    db.commit()
    return {"ok": True}