from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class PackingList(Base):
    __tablename__ = "packing_lists"

    id_packing_list = Column(Integer, primary_key=True, index=True)

    orden_compra_id = Column(
        Integer,
        ForeignKey("orden_compra.id_orden_compra", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    origen = Column(String(100))
    producto = Column(String(255))
    destino = Column(String(255))

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    orden_compra = relationship(
        "OrdenCompra",
        back_populates="packing_list",
    )

    guias = relationship(
        "PackingListGuia",
        back_populates="packing_list",
        cascade="all, delete-orphan",
        order_by="PackingListGuia.orden, PackingListGuia.id_packing_list_guia",
    )