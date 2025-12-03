from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class EstadoOe(Base):
    __tablename__ = "estado_oe"

    id_estado_oe = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)

    OperacionExportaciones = relationship(
        "OperacionExportacion",
        back_populates="EstadoOe",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    @staticmethod
    def attribute_labels():
        return {"id_estado_oe": "Id Estado Oe", "nombre": "Nombre"}

    def to_dict(self):
        return {"id_estado_oe": self.id_estado_oe, "nombre": self.nombre}

    def __repr__(self):
        return f"<EstadoOe {self.id_estado_oe} {self.nombre!r}>"
