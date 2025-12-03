from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, event, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class Puerto(Base):
    __tablename__ = "puerto"

    # PK
    id_puerto = Column(Integer, primary_key=True, autoincrement=True)

    # Campos (igual a rules() de Yii)
    nombre      = Column(String(200), nullable=False)  # required + unique
    descripcion = Column(String(200))
    id_ciudad   = Column(Integer, ForeignKey("ciudad.id_ciudad", ondelete=None), nullable=False)

    __table_args__ = (
        UniqueConstraint("nombre", name="uq_puerto_nombre"),  # nombre único (Yii: unique)
    )

    # ===== Relaciones (mismos nombres que en Yii) =====

    OperacionOrigen = relationship(
    "OperacionExportacion",
    foreign_keys="OperacionExportacion.id_puerto_origen",   # ← string (válido)
    back_populates="PuertoOrigen",
    lazy="dynamic",
    )
    OperacionDestino = relationship(
    "OperacionExportacion",
    foreign_keys="OperacionExportacion.id_puerto_destino",
    back_populates="PuertoDestino",
    lazy="dynamic",
    )
    
    # Utilidad opcional
    def to_dict(self):
        return {
            "id_puerto": self.id_puerto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "id_ciudad": self.id_ciudad,
        }

    def __repr__(self):
        return f"<Puerto {self.id_puerto} {self.nombre!r}>"


# ===== Callbacks para replicar beforeValidate (uppercase nombre) =====
def _uppercase_nombre(mapper, connection, target: Puerto):
    if target.nombre is not None:
        target.nombre = target.nombre.upper()

event.listen(Puerto, "before_insert", _uppercase_nombre)
event.listen(Puerto, "before_update", _uppercase_nombre)
