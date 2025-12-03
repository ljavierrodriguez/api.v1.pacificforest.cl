from sqlalchemy import Integer, String, Numeric, Column, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class DetallePl(Base):
    __tablename__ = "detalle_pl"

    id_detalle_pl = Column(Integer, primary_key=True)
    id_ple = Column(Integer, ForeignKey("ple.id_ple"), index=True)
    id_plc = Column(Integer, ForeignKey("plc.id_plc"), nullable=True)

    etiqueta = Column(String(20), nullable=False)
    descripcion = Column(String(100), nullable=False)

    id_unidad_venta = Column(Integer, ForeignKey("unidad_venta.id_unidad_venta"), nullable=False)
    cantidad = Column(Integer)

    espesor_ple = Column(String(20), nullable=False)
    id_unidad_medida_espesor_ple = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=False)

    ancho_ple = Column(String(20), nullable=False)
    id_unidad_medida_ancho_ple = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=False)

    largo_ple = Column(String(20), nullable=False)
    id_unidad_medida_largo_ple = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=False)

    piezas = Column(Integer, nullable=False)

    volumen_ple = Column(Numeric(12, 3), nullable=False)
    costo_eq_m3 = Column(Numeric(12, 3))
    costo_paquete = Column(Numeric(12, 3))

    id_estado_detalle_ple = Column(Integer, ForeignKey("estado_detalle_ple.id_estado_detalle_ple"), nullable=False)

    venta_eq_m3 = Column(Numeric(12, 3))
    venta_unitario = Column(Numeric(12, 3))
    venta_paquete = Column(Numeric(12, 3), nullable=False)

    operacion_exportacion = Column(Integer)
    odc = Column(Integer)

    id_unidad_medida_espesor_plc = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))
    id_unidad_medida_ancho_plc = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))
    id_unidad_medida_largo_plc = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    espesor_plc = Column(String(20))
    ancho_plc = Column(String(20))
    largo_plc = Column(String(20))
    volumen_plc = Column(Numeric(12, 3))

    costo_unitario = Column(Numeric(12, 3))
    pulgada_cubica = Column(Numeric(12, 3))
    metro_lineal = Column(Numeric(12, 3))
    pie = Column(Numeric(12, 3))

    Ple = relationship("Ple", back_populates="DetallePl", lazy="joined")
    UnidadVenta = relationship("UnidadVenta", back_populates="DetallePl", lazy="joined")

    UnidadMedidaAnchoPle = relationship("UnidadMedida", foreign_keys=[id_unidad_medida_ancho_ple], lazy="joined")
    UnidadMedidaEspesorPle = relationship("UnidadMedida", foreign_keys=[id_unidad_medida_espesor_ple], lazy="joined")
    UnidadMedidaLargoPle = relationship("UnidadMedida", foreign_keys=[id_unidad_medida_largo_ple], lazy="joined")

    UnidadMedidaAnchoPlc = relationship("UnidadMedida", foreign_keys=[id_unidad_medida_ancho_plc], lazy="joined")
    UnidadMedidaEspesorPlc = relationship("UnidadMedida", foreign_keys=[id_unidad_medida_espesor_plc], lazy="joined")
    UnidadMedidaLargoPlc = relationship("UnidadMedida", foreign_keys=[id_unidad_medida_largo_plc], lazy="joined")

    def __repr__(self):
        return f"<DetallePl id={self.id_detalle_pl} etiqueta={self.etiqueta}>"
