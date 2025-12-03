from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class EstadoOdc(Base):
    __tablename__ = "estado_odc"

    id_estado_odc = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(15), nullable=False)

    OrdenesCompra = relationship(
        "OrdenCompra",
        back_populates="EstadoOdc",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    def to_dict(self):
        return {
            "id_estado_odc": self.id_estado_odc,
            "nombre": self.nombre,
        }

    def __repr__(self):
        return f"<EstadoOdc {self.id_estado_odc} {self.nombre!r}>"
