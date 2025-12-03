from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.ide import Ide
from app.schemas.ide import IdeCreate, IdeRead, IdeUpdate

router = APIRouter(prefix="/ide", tags=["ide"])


@router.post("/", response_model=IdeRead, summary='POST Ide', description='POST Ide endpoint. Replace this placeholder with a meaningful description.')
def create_ide(payload: IdeCreate, db: Session = Depends(get_db)):
    obj = Ide(
        id_proforma=payload.id_proforma,
        id_tipo_envase=payload.id_tipo_envase,
        referencia=payload.referencia,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[IdeRead], summary='GET Ide', description='GET Ide endpoint. Replace this placeholder with a meaningful description.')
def list_ide(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Ide).offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=IdeRead, summary='GET Ide', description='GET Ide endpoint. Replace this placeholder with a meaningful description.')
def get_ide(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ide, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ide not found")
    return item


@router.put("/{item_id}", response_model=IdeRead, summary='PUT Ide', description='PUT Ide endpoint. Replace this placeholder with a meaningful description.')
def update_ide(item_id: int, payload: IdeUpdate, db: Session = Depends(get_db)):
    item = db.get(Ide, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ide not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Ide', description='DELETE Ide endpoint. Replace this placeholder with a meaningful description.')
def delete_ide(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Ide, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ide not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
