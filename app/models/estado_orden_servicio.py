from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class EstadoOrdenServicio(Base):
    __tablename__ = "estado_orden_servicio"

    id_estado_orden_servicio = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20), nullable=False)

    OrdenesServicio = relationship(
        "OrdenServicio",
        back_populates="EstadoOrdenServicio",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    def to_dict(self):
        return {
            "id_estado_orden_servicio": self.id_estado_orden_servicio,
            "nombre": self.nombre,
        }

    def __repr__(self):
        return f"<EstadoOrdenServicio {self.id_estado_orden_servicio} {self.nombre!r}>"
