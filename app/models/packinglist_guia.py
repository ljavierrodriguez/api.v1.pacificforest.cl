from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class PackingListGuia(Base):
    __tablename__ = "packing_list_guias"

    id_packing_list_guia = Column(Integer, primary_key=True, index=True)

    id_packing_list = Column(
        Integer,
        ForeignKey("packing_lists.id_packing_list", ondelete="CASCADE"),
        nullable=False,
    )

    guia_despacho = Column(String(100), nullable=False)
    fecha_despacho = Column(Date, nullable=False)
    orden = Column(Integer, nullable=False, default=0)

    packing_list = relationship(
        "PackingList",
        back_populates="guias",
    )

    detalles = relationship(
        "PackingListDetalle",
        back_populates="packing_list_guia",
        cascade="all, delete-orphan",
        order_by="PackingListDetalle.id_packing_list_detalle",
    )