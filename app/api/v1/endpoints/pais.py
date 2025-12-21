from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from app.schemas.pais import PaisCreate, PaisRead, PaisUpdate
from app.schemas.pagination import create_paginated_response
from app.models.pais import Pais
from app.db.session import get_db

router = APIRouter(prefix="/paises", tags=["paises"])


@router.post("/", response_model=PaisRead, summary='POST Pais', description='POST Pais endpoint. Replace this placeholder with a meaningful description.')
def create_pais(payload: PaisCreate, db: Session = Depends(get_db)):
    p = Pais(nombre=payload.nombre)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/", response_model=List[PaisRead], summary='GET Pais', description='GET Pais endpoint. Replace this placeholder with a meaningful description.')
def list_paises(db: Session = Depends(get_db)):
    return db.query(Pais).all()


@router.get("/{id_pais}", response_model=PaisRead, summary='GET Pais por id', description='Obtener un país por su id.')
def get_pais(id_pais: int, db: Session = Depends(get_db)):
    pais = db.query(Pais).filter(Pais.id_pais == id_pais).first()
    if not pais:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="País no encontrado")
    return pais


@router.put("/{id_pais}", response_model=PaisRead, summary='Actualizar Pais', description='Actualizar un país existente.')
def update_pais(id_pais: int, payload: PaisUpdate, db: Session = Depends(get_db)):
    pais = db.query(Pais).filter(Pais.id_pais == id_pais).first()
    if not pais:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="País no encontrado")

    if payload.nombre is not None:
        pais.nombre = payload.nombre

    db.add(pais)
    db.commit()
    db.refresh(pais)
    return pais


@router.delete("/{id_pais}", status_code=status.HTTP_204_NO_CONTENT, summary='Eliminar Pais', description='Eliminar un país por id.')
def delete_pais(id_pais: int, db: Session = Depends(get_db)):
    pais = db.query(Pais).filter(Pais.id_pais == id_pais).first()
    if not pais:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="País no encontrado")
    db.delete(pais)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
