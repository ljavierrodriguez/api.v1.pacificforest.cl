from sqlalchemy import Integer, String, Boolean, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.db.base import Base


class DetalleGasto(Base):
    __tablename__ = "detalle_gasto"

    id_detalle_gasto = Column(Integer, primary_key=True, autoincrement=True)
    id_gasto = Column(Integer, ForeignKey("gasto.id_gasto"), nullable=True)
    valor = Column(String(12), nullable=False)
    nro_documento = Column(String(50), nullable=True)
    pagado = Column(Boolean, nullable=False)

    Gasto = relationship(
        "Gasto",
        foreign_keys=[id_gasto],
        backref=backref("DetalleGastos", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<DetalleGasto {self.id_detalle_gasto} Gasto={self.id_gasto}>"
