from __future__ import annotations
from sqlalchemy import event, Column, Integer, String, ForeignKey, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from app.db.base import Base


class Ciudad(Base):
    __tablename__ = "ciudad"

    id_ciudad = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_pais = Column(Integer, ForeignKey("pais.id_pais"), nullable=False)
    nombre = Column(String(200), nullable=False, index=True)

    Empresas = relationship(
        "Empresa",
        backref="Ciudad",
        lazy=True,
        primaryjoin="Empresa.id_ciudad==Ciudad.id_ciudad",
    )
    Puertos = relationship(
        "Puerto",
        backref="Ciudad",
        lazy=True,
        primaryjoin="Puerto.id_ciudad==Ciudad.id_ciudad",
    )
    Pais = relationship("Pais", backref="Ciudades", lazy=True)

    def to_dict(self) -> dict:
        return {"id_ciudad": self.id_ciudad, "id_pais": self.id_pais, "nombre": self.nombre}

    def __repr__(self):
        return f"<Ciudad id={self.id_ciudad} nombre={self.nombre!r} pais={self.id_pais}>"


# Hooks and validations (using connection-level SQL similar to previous implementation)
def _toupper_nombre(target: Ciudad):
    if target.nombre:
        target.nombre = target.nombre.strip().upper()


def _validate_unique_nombre(connection, target: Ciudad):
    sql = text("SELECT 1 FROM ciudad WHERE nombre = :nombre AND id_ciudad <> :id")
    params = {"nombre": target.nombre, "id": target.id_ciudad or 0}
    exists = connection.execute(sql, params).scalar()
    if exists:
        raise ValueError("El nombre de la ciudad ya existe")


@event.listens_for(Ciudad, "before_insert")
def _ciudad_before_insert(mapper, connection, target: Ciudad):
    _toupper_nombre(target)
    _validate_unique_nombre(connection, target)


@event.listens_for(Ciudad, "before_update")
def _ciudad_before_update(mapper, connection, target: Ciudad):
    _toupper_nombre(target)
    _validate_unique_nombre(connection, target)
