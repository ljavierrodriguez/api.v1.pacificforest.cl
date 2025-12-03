from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref
from app.db.base import Base


class EstadoDetallePle(Base):
    __tablename__ = "estado_detalle_ple"

    id_estado_detalle_ple = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(15), nullable=False)

    DetallePls = relationship(
        "DetallePl",
        backref=backref("EstadoDetallePle"),
        lazy="dynamic",
        foreign_keys="DetallePl.id_estado_detalle_ple",
    )

    def __repr__(self):
        return f"<EstadoDetallePle {self.id_estado_detalle_ple} {self.nombre}>"
