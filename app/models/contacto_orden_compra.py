from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class ContactoOrdenCompra(Base):
    __tablename__ = "contacto_orden_compra"

    id_contacto_orden_compra = Column(Integer, primary_key=True, index=True)
    id_orden_compra = Column(Integer, ForeignKey("orden_compra.id_orden_compra", ondelete="CASCADE"), index=True)
    id_contacto = Column(Integer, ForeignKey("contacto.id_contacto", ondelete="CASCADE"), index=True)

    OrdenCompra = relationship("OrdenCompra", back_populates="ContactosOrdenCompra")
    Contacto = relationship("Contacto", back_populates="ContactoOrdenesCompra")

    def to_dict(self) -> dict:
        return {
            "id_contacto_orden_compra": self.id_contacto_orden_compra,
            "id_orden_compra": self.id_orden_compra,
            "id_contacto": self.id_contacto,
        }

    def __repr__(self) -> str:
        return f"<ContactoOrdenCompra id={self.id_contacto_orden_compra} oc={self.id_orden_compra} contacto={self.id_contacto}>"
