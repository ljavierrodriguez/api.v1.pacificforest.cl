from sqlalchemy import Integer, String, Numeric, ForeignKey, event, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class DetalleOrdenServicio(Base):
    __tablename__ = "detalle_orden_servicio"

    id_detalle_os = Column(Integer, primary_key=True, autoincrement=True)

    id_orden_servicio = Column(Integer, ForeignKey("orden_servicio.id_orden_servicio"), nullable=False)
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
    precio_unitario = Column(Numeric(12, 3), nullable=False)
    subtotal = Column(Numeric(12, 3))

    volumen = Column(Numeric(12, 3))
    volumen_eq = Column(Numeric(12, 3))
    precio_eq = Column(Numeric(12, 3))

    OrdenServicio = relationship(
        "OrdenServicio",
        back_populates="DetalleOrdenServicio",
        foreign_keys=[id_orden_servicio],
    )
    Producto = relationship(
        "Producto",
        primaryjoin="foreign(DetalleOrdenServicio.id_producto)==Producto.id_producto",
        viewonly=True,
    )
    UnidadVenta = relationship(
        "UnidadVenta",
        primaryjoin="foreign(DetalleOrdenServicio.id_unidad_venta)==UnidadVenta.id_unidad_venta",
        viewonly=True,
    )
    UnidadMedidaEspesor = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleOrdenServicio.id_unidad_medida_espesor)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaAncho = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleOrdenServicio.id_unidad_medida_ancho)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaLargo = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleOrdenServicio.id_unidad_medida_largo)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )


@event.listens_for(DetalleOrdenServicio, "before_insert")
@event.listens_for(DetalleOrdenServicio, "before_update")
def _round_vols(mapper, connection, target: DetalleOrdenServicio):
    def _round3(v):
        if v is None:
            return None
        try:
            return round(float(v), 3)
        except Exception:
            return v

    target.volumen_eq = _round3(target.volumen_eq)
    target.volumen = _round3(target.volumen)
