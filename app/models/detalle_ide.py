from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.db.base import Base


class DetalleIde(Base):
    __tablename__ = "detalle_ide"

    id_detalle_ide = Column(Integer, primary_key=True, autoincrement=True)

    id_ide = Column(Integer, ForeignKey("ide.id_ide"), nullable=False)
    id_plc = Column(Integer, ForeignKey("plc.id_plc"), nullable=False)
    fob = Column(String(12), nullable=False)
    identificador_contenedor = Column(String(50), nullable=True)
    sello = Column(String(50), nullable=True)
    peso_neto = Column(String(12), nullable=True)
    peso_bruto = Column(String(12), nullable=True)
    nro_linea = Column(Integer, nullable=False)

    Ide = relationship(
        "Ide",
        foreign_keys=[id_ide],
        backref=backref("DetalleIdes", lazy="dynamic"),
    )

    Plc = relationship(
        "Plc",
        foreign_keys=[id_plc],
        backref=backref("DetalleIde", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<DetalleIde {self.id_detalle_ide} IDE={self.id_ide} PLC={self.id_plc} nro={self.nro_linea}>"
