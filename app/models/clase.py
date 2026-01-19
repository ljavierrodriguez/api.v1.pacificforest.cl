from __future__ import annotations
from sqlalchemy import event, Column, Integer, String, text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Clase(Base):
    __tablename__ = "clase"

    id_clase = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(String(100))

    # Relaciones (actívalas cuando tengas el modelo Producto):
    Productos = relationship(
        "Producto",
        backref="clase",
        lazy=True,
        primaryjoin="Producto.id_clase==Clase.id_clase",
    )

    def to_dict(self) -> dict:
        return {"id_clase": self.id_clase, "nombre": self.nombre, "descripcion": self.descripcion}

    def __repr__(self):
        return f"<Clase id={self.id_clase} nombre={self.nombre!r}>"


# ---- Hooks: uppercase nombre + uniqueness validation at connection level ----
def _toupper_nombre(target: Clase):
    if target.nombre:
        target.nombre = target.nombre.strip().upper()


def _validate_unique_nombre(connection, target: Clase):
    sql = text("SELECT 1 FROM clase WHERE nombre = :nombre AND id_clase <> :id")
    params = {"nombre": target.nombre, "id": target.id_clase or 0}
    exists = connection.execute(sql, params).scalar()
    if exists:
        raise ValueError("El nombre de la clase ya existe")


@event.listens_for(Clase, "before_insert")
def _clase_before_insert(mapper, connection, target: Clase):
    _toupper_nombre(target)
    _validate_unique_nombre(connection, target)


@event.listens_for(Clase, "before_update")
def _clase_before_update(mapper, connection, target: Clase):
    _toupper_nombre(target)
    _validate_unique_nombre(connection, target)
