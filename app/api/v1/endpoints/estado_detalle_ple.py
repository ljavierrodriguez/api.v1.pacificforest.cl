from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.estado_detalle_ple import EstadoDetallePle
from app.schemas.estado_detalle_ple import EstadoDetallePleCreate, EstadoDetallePleRead
from app.db.session import get_db

router = APIRouter(prefix="/estados-detalle-ple", tags=["estado_detalle_ple"])


@router.post("/", response_model=EstadoDetallePleRead, status_code=201, summary='POST Estado Detalle Ple', description='POST Estado Detalle Ple endpoint. Replace this placeholder with a meaningful description.')
def create_estado(payload: EstadoDetallePleCreate, db: Session = Depends(get_db)):
    obj = EstadoDetallePle(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[EstadoDetallePleRead], summary='GET Estado Detalle Ple', description='GET Estado Detalle Ple endpoint. Replace this placeholder with a meaningful description.')
def list_estados(db: Session = Depends(get_db)):
    return db.query(EstadoDetallePle).all()
