from datetime import date
from sqlalchemy import Integer, String, Date, Numeric, ForeignKey, event, select, func, Column
from sqlalchemy.orm import relationship, validates
from app.db.base import Base


class OrdenServicio(Base):
    __tablename__ = "orden_servicio"

    id_orden_servicio = Column(Integer, primary_key=True)

    fecha_emision = Column(Date, nullable=False)
    fecha_entrega = Column(Date, nullable=False)

    id_cliente_proveedor = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    id_usuario_encargado = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)

    id_bodega = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=False)
    destino = Column(String(15))

    id_moneda = Column(Integer, ForeignKey("moneda.id_moneda"), nullable=False)
    id_empresa = Column(Integer, ForeignKey("empresa.id_empresa"))
    id_direccion_proveedor = Column(Integer, ForeignKey("direccion.id_direccion"), nullable=False)

    observacion = Column(String(1000))
    nota_1 = Column(String(1000))
    otras_especificaciones = Column(String(1000))
    url_imagen = Column(String(100))

    valor_neto = Column(Numeric(13, 3), nullable=False)
    iva = Column(Numeric(12, 3), nullable=False)
    tasa_iva = Column(Numeric(6, 3))
    valor_total = Column(Numeric(12, 3), nullable=False)

    id_estado_orden_servicio = Column(
        Integer,
        ForeignKey("estado_orden_servicio.id_estado_orden_servicio"),
        nullable=False,
    )

    DetalleOrdenServicio = relationship(
        "DetalleOrdenServicio",
        back_populates="OrdenServicio",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    ClienteProveedor = relationship(
        "ClienteProveedor",
        foreign_keys=[id_cliente_proveedor],
    )
    Usuario = relationship("User", foreign_keys=[id_usuario])
    UsuarioEncargado = relationship("User", foreign_keys=[id_usuario_encargado])
    Empresa = relationship("Empresa")
    Moneda = relationship("Moneda")
    Bodega = relationship("Bodega")
    DireccionProveedor = relationship("Direccion")
    EstadoOrdenServicio = relationship(
        "EstadoOrdenServicio",
        back_populates="OrdenesServicio",
        foreign_keys=[id_estado_orden_servicio],
    )

    @validates("fecha_entrega", "fecha_emision")
    def _validate_fechas(self, key, value):
        if key == "fecha_entrega" and value and self.fecha_emision and value < self.fecha_emision:
            raise ValueError("Fecha de entrega no puede ser menor a fecha de emisión")
        return value

    @validates("valor_neto", "valor_total", "iva")
    def _round_montos(self, key, value):
        if value is None:
            return None
        from decimal import Decimal, ROUND_HALF_UP
        return Decimal(value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    def serialize(self) -> dict:
        to_str = lambda d: d.isoformat() if isinstance(d, date) and d else None
        as_float = lambda x: float(x) if x is not None else None
        return {
            "id_orden_servicio": self.id_orden_servicio,
            "fecha_emision": to_str(self.fecha_emision),
            "fecha_entrega": to_str(self.fecha_entrega),
            "id_cliente_proveedor": self.id_cliente_proveedor,
            "id_usuario_encargado": self.id_usuario_encargado,
            "id_usuario": self.id_usuario,
            "id_bodega": self.id_bodega,
            "destino": self.destino,
            "id_moneda": self.id_moneda,
            "id_empresa": self.id_empresa,
            "id_direccion_proveedor": self.id_direccion_proveedor,
            "observacion": self.observacion,
            "nota_1": self.nota_1,
            "otras_especificaciones": self.otras_especificaciones,
            "url_imagen": self.url_imagen,
            "valor_neto": as_float(self.valor_neto),
            "iva": as_float(self.iva),
            "tasa_iva": as_float(self.tasa_iva),
            "valor_total": as_float(self.valor_total),
            "id_estado_orden_servicio": self.id_estado_orden_servicio,
        }

    def __repr__(self) -> str:
        return f"<OrdenServicio id={self.id_orden_servicio}>"


@event.listens_for(OrdenServicio, "before_insert")
def _assign_pk_before_insert(mapper, connection, target: OrdenServicio):
    if target.id_orden_servicio is None:
        next_id = connection.execute(
            select(func.coalesce(func.max(OrdenServicio.id_orden_servicio), 0) + 1)
        ).scalar_one()
        target.id_orden_servicio = max(next_id, 3000)
