from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.parametro import Parametro
from app.schemas.parametro import ParametroCreate, ParametroRead
from app.schemas.pagination import create_paginated_response
from app.db.session import get_db

router = APIRouter(prefix="/parametros", tags=["parametros"])


@router.post("/", response_model=ParametroRead, status_code=201, summary='POST Parametro', description='POST Parametro endpoint. Replace this placeholder with a meaningful description.')
def create_parametro(payload: ParametroCreate, db: Session = Depends(get_db)):
    obj = Parametro(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/", response_model=List[ParametroRead], summary='GET Parametro', description='GET Parametro endpoint. Replace this placeholder with a meaningful description.')
def list_parametros(db: Session = Depends(get_db)):
    return db.query(Parametro).all()
