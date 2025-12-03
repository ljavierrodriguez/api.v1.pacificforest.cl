from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref
from app.db.base import Base


class Bodega(Base):
    __tablename__ = "bodega"

    id_bodega = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(200), nullable=False, unique=True)
    direccion = Column(String(200), nullable=True)

    # HAS_MANY -> OrdenCompra.id_bodega
    OrdenCompras = relationship(
        "OrdenCompra",
        backref=backref("Bodega"),
        lazy="dynamic",
        foreign_keys="OrdenCompra.id_bodega",
    )

    Ides = relationship(
        "Ide",
        back_populates="Bodega",
        lazy="dynamic",
        foreign_keys="Ide.id_bodega",
    )

    def __repr__(self):
        return f"<Bodega {self.id_bodega} {self.nombre!r}>"
