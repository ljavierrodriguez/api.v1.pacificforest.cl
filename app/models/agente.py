from __future__ import annotations
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, event, update as sa_update
from sqlalchemy.orm import relationship
from app.db.base import Base


class Agente(Base):
    __tablename__ = "agente"

    id_agente = Column(Integer, primary_key=True, index=True)
    id_pais = Column(Integer, ForeignKey("pais.id_pais"), nullable=False)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100))
    telefono = Column(String(50))
    por_defecto = Column(Boolean, default=False, nullable=False)

    # Relaciones
    Pais = relationship("Pais", back_populates="Agentes")
    proformas = relationship("Proforma", back_populates="Agente")

    def to_dict(self) -> dict:
        return {
            "id_agente": self.id_agente,
            "id_pais": self.id_pais,
            "nombre": self.nombre,
            "correo": self.correo,
            "telefono": self.telefono,
            "por_defecto": self.por_defecto,
        }

    def __repr__(self):
        return f"<Agente id={self.id_agente} nombre={self.nombre!r} pais={self.id_pais} default={self.por_defecto}>"


# Mantener lógica de exclusividad de `por_defecto` usando eventos de SQLAlchemy
@event.listens_for(Agente, "after_insert")
def _agente_after_insert(mapper, connection, target: Agente):
    if target.por_defecto:
        stmt = (
            sa_update(Agente.__table__)
            .where(Agente.c.id_agente != target.id_agente)
            .where(Agente.c.por_defecto == True)
            .values(por_defecto=False)
        )
        connection.execute(stmt)


@event.listens_for(Agente, "after_update")
def _agente_after_update(mapper, connection, target: Agente):
    if target.por_defecto:
        stmt = (
            sa_update(Agente.__table__)
            .where(Agente.c.id_agente != target.id_agente)
            .where(Agente.c.por_defecto == True)
            .values(por_defecto=False)
        )
        connection.execute(stmt)
