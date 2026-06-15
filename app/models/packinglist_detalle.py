from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class PackingListDetalle(Base):
    __tablename__ = "packing_list_detalles"

    id_packing_list_detalle = Column(Integer, primary_key=True, index=True)

    packing_list_id = Column(
        Integer,
        ForeignKey("packing_lists.id_packing_list", ondelete="CASCADE"),
        nullable=False,
    )

    id_packing_list_guia = Column(
        Integer,
        ForeignKey("packing_list_guias.id_packing_list_guia", ondelete="CASCADE"),
        nullable=False,
    )

    oc = Column(String(100))
    etiqueta = Column(String(100))
    numero_pqts = Column(Integer)

    espesor = Column(Numeric(10, 2))
    ancho = Column(Numeric(10, 2))
    largo = Column(Numeric(10, 2))

    piezas = Column(Integer)
    origen_detalle = Column(String(100))

    packing_list = relationship("PackingList")

    packing_list_guia = relationship(
        "PackingListGuia",
        back_populates="detalles",
    )