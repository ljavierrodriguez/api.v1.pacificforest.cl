from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.schemas.agente import AgenteCreate, AgenteRead, AgenteUpdate
from app.models.agente import Agente
from app.db.session import get_db

router = APIRouter(prefix="/agentes", tags=["agentes"])


@router.post("/", response_model=AgenteRead, status_code=201, summary='POST Agente', description='POST Agente endpoint. Replace this placeholder with a meaningful description.')
def create_agente(payload: AgenteCreate, db: Session = Depends(get_db)):
    a = Agente(
        id_pais=payload.id_pais,
        nombre=payload.nombre,
        correo=str(payload.correo) if payload.correo else None,
        telefono=payload.telefono,
        por_defecto=payload.por_defecto or False,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.get("/", response_model=List[AgenteRead], summary='GET Agente', description='GET Agente endpoint. Replace this placeholder with a meaningful description.')
def list_agentes(db: Session = Depends(get_db)):
    return db.query(Agente).all()


@router.get("/{id_agente}", response_model=AgenteRead, summary='GET Agente por id', description='Obtener un agente por su id.')
def get_agente(id_agente: int, db: Session = Depends(get_db)):
    agente = db.query(Agente).filter(Agente.id_agente == id_agente).first()
    if not agente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente no encontrado")
    return agente


@router.put("/{id_agente}", response_model=AgenteRead, summary='Actualizar Agente', description='Actualizar un agente existente.')
def update_agente(id_agente: int, payload: AgenteUpdate, db: Session = Depends(get_db)):
    agente = db.query(Agente).filter(Agente.id_agente == id_agente).first()
    if not agente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente no encontrado")

    # Actualizar sólo campos provistos
    if payload.id_pais is not None:
        agente.id_pais = payload.id_pais
    if payload.nombre is not None:
        agente.nombre = payload.nombre
    if payload.correo is not None:
        agente.correo = str(payload.correo) if payload.correo else None
    if payload.telefono is not None:
        agente.telefono = payload.telefono
    if payload.por_defecto is not None:
        agente.por_defecto = payload.por_defecto

    db.add(agente)
    db.commit()
    db.refresh(agente)
    return agente


@router.delete("/{id_agente}", status_code=status.HTTP_204_NO_CONTENT, summary='Eliminar Agente', description='Eliminar un agente por id.')
def delete_agente(id_agente: int, db: Session = Depends(get_db)):
    agente = db.query(Agente).filter(Agente.id_agente == id_agente).first()
    if not agente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente no encontrado")
    db.delete(agente)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
