from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.documento_ide import DocumentoIde
from app.schemas.documento_ide import (
    DocumentoIdeCreate,
    DocumentoIdeRead,
    DocumentoIdeUpdate,
)

router = APIRouter(prefix="/documento_ide", tags=["documento_ide"])


@router.post("/", response_model=DocumentoIdeRead, summary='POST Documento Ide', description='POST Documento Ide endpoint. Replace this placeholder with a meaningful description.')
def create_documento_ide(payload: DocumentoIdeCreate, db: Session = Depends(get_db)):
    obj = DocumentoIde(
        id_ide=payload.id_ide,
        descripcion=payload.descripcion,
        nombre_original=payload.nombre_original,
        nombre_archivo=payload.nombre_archivo,
        enviado=payload.enviado,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[DocumentoIdeRead], summary='GET Documento Ide', description='GET Documento Ide endpoint. Replace this placeholder with a meaningful description.')
def list_documento_ide(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(DocumentoIde).offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=DocumentoIdeRead, summary='GET Documento Ide', description='GET Documento Ide endpoint. Replace this placeholder with a meaningful description.')
def get_documento_ide(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DocumentoIde, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DocumentoIde not found")
    return item


@router.put("/{item_id}", response_model=DocumentoIdeRead, summary='PUT Documento Ide', description='PUT Documento Ide endpoint. Replace this placeholder with a meaningful description.')
def update_documento_ide(item_id: int, payload: DocumentoIdeUpdate, db: Session = Depends(get_db)):
    item = db.get(DocumentoIde, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DocumentoIde not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", summary='DELETE Documento Ide', description='DELETE Documento Ide endpoint. Replace this placeholder with a meaningful description.')
def delete_documento_ide(item_id: int, db: Session = Depends(get_db)):
    item = db.get(DocumentoIde, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="DocumentoIde not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
