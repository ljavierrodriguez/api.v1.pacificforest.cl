from sqlalchemy import Integer, ForeignKey, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class ContactoOrdenServicio(Base):
    __tablename__ = "contacto_orden_servicio"

    id_contacto_orden_servicio = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_contacto = Column(Integer, ForeignKey("contacto.id_contacto", ondelete="CASCADE"), nullable=False, index=True)
    id_orden_servicio = Column(Integer, ForeignKey("orden_servicio.id_orden_servicio", ondelete="CASCADE"), nullable=False, index=True)

    Contacto = relationship(
        "Contacto",
        primaryjoin="foreign(ContactoOrdenServicio.id_contacto)==Contacto.id_contacto",
        back_populates="ContactosOrdenServicio",
    )
    OrdenServicio = relationship(
        "OrdenServicio",
        primaryjoin="foreign(ContactoOrdenServicio.id_orden_servicio)==OrdenServicio.id_orden_servicio",
        back_populates="ContactosOrdenServicio",
    )

    def to_dict(self) -> dict:
        return {
            "id_contacto_orden_servicio": self.id_contacto_orden_servicio,
            "id_contacto": self.id_contacto,
            "id_orden_servicio": self.id_orden_servicio,
        }

    def __repr__(self) -> str:
        return f"<ContactoOrdenServicio id={self.id_contacto_orden_servicio} os={self.id_orden_servicio} contacto={self.id_contacto}>"
