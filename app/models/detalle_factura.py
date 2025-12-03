from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class DetalleFactura(Base):
    __tablename__ = "detalle_factura"

    id_detalle_factura = Column(Integer, primary_key=True, autoincrement=True)
    id_factura = Column(Integer, ForeignKey("factura.id_factura"), nullable=False)

    cantidad = Column(String(12), nullable=False)
    especificaciones = Column(String(300), nullable=False)
    precio_unitario = Column(String(12), nullable=False)
    total = Column(String(12), nullable=False)

    Factura = relationship(
        "Factura",
        back_populates="DetalleFactura",
        foreign_keys=[id_factura],
    )

    def __repr__(self):
        return f"<DetalleFactura {self.id_detalle_factura} factura={self.id_factura}>"

    def to_dict(self):
        return {
            "id_detalle_factura": self.id_detalle_factura,
            "id_factura": self.id_factura,
            "cantidad": self.cantidad,
            "especificaciones": self.especificaciones,
            "precio_unitario": self.precio_unitario,
            "total": self.total,
        }
