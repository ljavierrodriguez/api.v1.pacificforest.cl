from sqlalchemy import Integer, String, Numeric, ForeignKey, event, Column
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base
from app.models.unidad_medida import UnidadMedida


class DetalleOrdenCompra(Base):
    __tablename__ = "detalle_orden_compra"

    id_detalle_odc = Column(Integer, primary_key=True, autoincrement=True)

    id_orden_compra = Column(Integer, ForeignKey("orden_compra.id_orden_compra"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"))
    id_unidad_venta = Column(Integer, ForeignKey("unidad_venta.id_unidad_venta"))

    texto_abierto = Column(String(200))

    espesor = Column(String(20))
    id_unidad_medida_espesor = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    ancho = Column(String(20))
    id_unidad_medida_ancho = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    largo = Column(String(20))
    id_unidad_medida_largo = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    cantidad = Column(Numeric(12, 3))
    precio_unitario = Column(Numeric(12, 3))
    subtotal = Column(Numeric(12, 3))

    volumen = Column(Numeric(12, 3))
    volumen_eq = Column(Numeric(12, 3))
    precio_eq = Column(Numeric(12, 3))

    odc_salida = Column(Integer)

    UnidadMedidaLargo = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleOrdenCompra.id_unidad_medida_largo)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaEspesor = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleOrdenCompra.id_unidad_medida_espesor)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaAncho = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleOrdenCompra.id_unidad_medida_ancho)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadVenta = relationship(
        "UnidadVenta",
        primaryjoin="foreign(DetalleOrdenCompra.id_unidad_venta)==UnidadVenta.id_unidad_venta",
        viewonly=True,
    )
    Producto = relationship(
        "Producto",
        primaryjoin="foreign(DetalleOrdenCompra.id_producto)==Producto.id_producto",
        viewonly=True,
    )
    OrdenCompra = relationship(
        "OrdenCompra",
        primaryjoin="foreign(DetalleOrdenCompra.id_orden_compra)==OrdenCompra.id_orden_compra",
        viewonly=True,
    )

    def __repr__(self):
        return f"<DetalleOrdenCompra {self.id_detalle_odc}>"

    def to_dict(self):
        def _num(x):
            return float(x) if x is not None else None

        return {
            "id_detalle_odc": self.id_detalle_odc,
            "id_orden_compra": self.id_orden_compra,
            "id_producto": self.id_producto,
            "texto_abierto": self.texto_abierto,
            "id_unidad_venta": self.id_unidad_venta,
            "cantidad": _num(self.cantidad),
            "espesor": self.espesor,
            "id_unidad_medida_espesor": self.id_unidad_medida_espesor,
            "ancho": self.ancho,
            "id_unidad_medida_ancho": self.id_unidad_medida_ancho,
            "largo": self.largo,
            "id_unidad_medida_largo": self.id_unidad_medida_largo,
            "precio_unitario": _num(self.precio_unitario),
            "subtotal": _num(self.subtotal),
            "volumen": _num(self.volumen),
            "volumen_eq": _num(self.volumen_eq),
            "precio_eq": _num(self.precio_eq),
            "odc_salida": self.odc_salida,
        }


@event.listens_for(DetalleOrdenCompra, "before_insert")
@event.listens_for(DetalleOrdenCompra, "before_update")
def _round_vols(mapper, connection, target: DetalleOrdenCompra):
    def _round3(v):
        if v is None:
            return None
        try:
            return round(float(v), 3)
        except Exception:
            return v

    target.volumen_eq = _round3(target.volumen_eq)
    target.volumen = _round3(target.volumen)
