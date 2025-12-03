from sqlalchemy import Integer, String, ForeignKey, event, Column
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base


class DetalleProforma(Base):
    __tablename__ = "detalle_proforma"

    id_detalle_proforma = Column(Integer, primary_key=True, autoincrement=True)

    id_proforma = Column(Integer, ForeignKey("proforma.id_proforma"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"))
    id_unidad_venta = Column(Integer, ForeignKey("unidad_venta.id_unidad_venta"), nullable=False)

    texto_libre = Column(String(200))

    espesor = Column(String(20))
    id_unidad_medida_espesor = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    ancho = Column(String(20))
    id_unidad_medida_ancho = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    largo = Column(String(20))
    id_unidad_medida_largo = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    piezas = Column(Integer)

    cantidad = Column(String(12), nullable=False)
    precio_unitario = Column(String(12), nullable=False)
    subtotal = Column(String(12), nullable=False)
    volumen = Column(String(12))
    volumen_eq = Column(String(12), nullable=False)
    precio_eq = Column(String(12), nullable=False)

    Proforma = relationship(
        "Proforma",
        primaryjoin="foreign(DetalleProforma.id_proforma)==Proforma.id_proforma",
        back_populates="DetalleProforma",
    )
    Producto = relationship(
        "Producto",
        primaryjoin="foreign(DetalleProforma.id_producto)==Producto.id_producto",
        viewonly=True,
    )
    UnidadVenta = relationship(
        "UnidadVenta",
        primaryjoin="foreign(DetalleProforma.id_unidad_venta)==UnidadVenta.id_unidad_venta",
        viewonly=True,
    )
    UnidadMedidaEspesor = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleProforma.id_unidad_medida_espesor)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaAncho = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleProforma.id_unidad_medida_ancho)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaLargo = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleProforma.id_unidad_medida_largo)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )

    def __repr__(self):
        return f"<DetalleProforma {self.id_detalle_proforma}>"

    def to_dict(self):
        return {
            "id_detalle_proforma": self.id_detalle_proforma,
            "id_proforma": self.id_proforma,
            "id_producto": self.id_producto,
            "texto_libre": self.texto_libre,
            "id_unidad_venta": self.id_unidad_venta,
            "cantidad": self.cantidad,
            "espesor": self.espesor,
            "id_unidad_medida_espesor": self.id_unidad_medida_espesor,
            "ancho": self.ancho,
            "id_unidad_medida_ancho": self.id_unidad_medida_ancho,
            "largo": self.largo,
            "id_unidad_medida_largo": self.id_unidad_medida_largo,
            "piezas": self.piezas,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
            "volumen": self.volumen,
            "volumen_eq": self.volumen_eq,
            "precio_eq": self.precio_eq,
        }



# ===== Hook equivalente a beforeValidate() de Yii =====
@event.listens_for(DetalleProforma, "before_insert")
@event.listens_for(DetalleProforma, "before_update")
def _round_vols(mapper, connection, target: DetalleProforma):
    def _round3_str(v):
        if v is None or str(v).strip() == "":
            return v
        try:
            n = round(float(str(v).replace(",", ".")), 3)
            s = f"{n:.3f}".rstrip("0").rstrip(".")
            return s
        except Exception:
            return v

    target.volumen_eq = _round3_str(target.volumen_eq)
    target.volumen = _round3_str(target.volumen)
