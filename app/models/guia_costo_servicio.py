from datetime import date
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base

# Tabla de asociación M:N entre Guía de Costo y Orden de Servicio
guia_costo_servicio_os = Table(
    "guia_costo_servicio_os",
    Base.metadata,
    Column("id_guia_costo_servicio", Integer, ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"), primary_key=True),
    Column("id_orden_servicio", Integer, ForeignKey("orden_servicio.id_orden_servicio", ondelete="CASCADE"), primary_key=True),
)

# Tabla de asociación M:N entre Guía de Costo y Orden de Compra
guia_costo_servicio_oc = Table(
    "guia_costo_servicio_oc",
    Base.metadata,
    Column("id_guia_costo_servicio", Integer, ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"), primary_key=True),
    Column("id_orden_compra", Integer, ForeignKey("orden_compra.id_orden_compra", ondelete="CASCADE"), primary_key=True),
)


class GuiaCostoServicio(Base):
    __tablename__ = "guia_costo_servicio"

    id_guia_costo_servicio = Column(Integer, primary_key=True, index=True)
    numero_guia = Column(String(100), nullable=False, index=True)
    fecha_despacho = Column(Date, nullable=True)
    fecha_registro = Column(Date, default=date.today)
    origen = Column(String(100), nullable=True)
    producto = Column(String(100), nullable=True)
    destino = Column(String(100), nullable=True)
    oc_compra_ref = Column(String(200), nullable=True)

    total_m3 = Column(Numeric(12, 4), nullable=True)
    total_usd = Column(Numeric(12, 2), nullable=True)
    observaciones = Column(Text, nullable=True)
    url_documento = Column(String(500), nullable=True)

    # Relaciones
    detalles = relationship(
        "DetalleCostoServicio",
        back_populates="guia_costo",
        cascade="all, delete-orphan",
        order_by="DetalleCostoServicio.id_detalle_costo_servicio",
    )

    productos_terminados = relationship(
        "GuiaCostoProductoTerminado",
        back_populates="guia_costo",
        cascade="all, delete-orphan",
        order_by="GuiaCostoProductoTerminado.id_producto_terminado",
    )

    detalles_proceso = relationship(
        "GuiaCostoDetalleProceso",
        back_populates="guia_costo",
        cascade="all, delete-orphan",
        order_by="GuiaCostoDetalleProceso.id_detalle_proceso",
    )

    ordenes_servicio = relationship(
        "OrdenServicio",
        secondary=guia_costo_servicio_os,
        lazy="joined",
    )

    ordenes_compra = relationship(
        "OrdenCompra",
        secondary=guia_costo_servicio_oc,
        lazy="joined",
    )

    def __repr__(self):
        return f"<GuiaCostoServicio {self.id_guia_costo_servicio} - Guia {self.numero_guia}>"

    def to_dict(self):
        detalles_list = [d.to_dict() for d in self.detalles] if self.detalles else []
        prod_term_list = [p.to_dict() for p in self.productos_terminados] if self.productos_terminados else []
        proceso_list = [pr.to_dict() for pr in self.detalles_proceso] if self.detalles_proceso else []

        os_ids = [os.id_orden_servicio for os in self.ordenes_servicio] if self.ordenes_servicio else []
        oc_ids = [oc.id_orden_compra for oc in self.ordenes_compra] if self.ordenes_compra else []

        calc_total_usd = sum(d.get("total_usd") or 0 for d in detalles_list)

        return {
            "id_guia_costo_servicio": self.id_guia_costo_servicio,
            "numero_guia": self.numero_guia,
            "fecha_despacho": self.fecha_despacho.isoformat() if self.fecha_despacho else None,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "origen": self.origen,
            "producto": self.producto,
            "destino": self.destino,
            "oc_compra_ref": self.oc_compra_ref,
            "total_m3": float(self.total_m3) if self.total_m3 is not None else None,
            "total_usd": float(self.total_usd) if self.total_usd is not None else round(calc_total_usd, 2),
            "observaciones": self.observaciones,
            "url_documento": self.url_documento,
            "ordenes_servicio_ids": os_ids,
            "ordenes_compra_ids": oc_ids,
            "detalles": detalles_list,
            "productos_terminados": prod_term_list,
            "detalles_proceso": proceso_list,
        }


class DetalleCostoServicio(Base):
    __tablename__ = "detalle_costo_servicio"

    id_detalle_costo_servicio = Column(Integer, primary_key=True, index=True)
    id_guia_costo_servicio = Column(
        Integer,
        ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
        nullable=False,
    )
    servicio = Column(String(200), nullable=False)
    volumen_m3 = Column(Numeric(12, 4), nullable=True)
    tarifa_usd_m3 = Column(Numeric(12, 4), nullable=True)
    total_usd = Column(Numeric(12, 2), nullable=True)

    guia_costo = relationship("GuiaCostoServicio", back_populates="detalles")

    def __repr__(self):
        return f"<DetalleCostoServicio {self.id_detalle_costo_servicio} - {self.servicio}>"

    def to_dict(self):
        return {
            "id_detalle_costo_servicio": self.id_detalle_costo_servicio,
            "id_guia_costo_servicio": self.id_guia_costo_servicio,
            "servicio": self.servicio,
            "volumen_m3": float(self.volumen_m3) if self.volumen_m3 is not None else None,
            "tarifa_usd_m3": float(self.tarifa_usd_m3) if self.tarifa_usd_m3 is not None else None,
            "total_usd": float(self.total_usd) if self.total_usd is not None else None,
        }


class GuiaCostoProductoTerminado(Base):
    __tablename__ = "guia_costo_producto_terminado"

    id_producto_terminado = Column(Integer, primary_key=True, index=True)
    id_guia_costo_servicio = Column(
        Integer,
        ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
        nullable=False,
    )
    espesor = Column(Numeric(8, 2), nullable=True)
    ancho = Column(Numeric(8, 2), nullable=True)
    largo = Column(Numeric(8, 2), nullable=True)
    piezas = Column(Integer, nullable=True)
    volumen_m3 = Column(Numeric(12, 4), nullable=True)

    guia_costo = relationship("GuiaCostoServicio", back_populates="productos_terminados")

    def to_dict(self):
        return {
            "id_producto_terminado": self.id_producto_terminado,
            "id_guia_costo_servicio": self.id_guia_costo_servicio,
            "espesor": float(self.espesor) if self.espesor is not None else None,
            "ancho": float(self.ancho) if self.ancho is not None else None,
            "largo": float(self.largo) if self.largo is not None else None,
            "piezas": self.piezas,
            "volumen_m3": float(self.volumen_m3) if self.volumen_m3 is not None else None,
        }


class GuiaCostoDetalleProceso(Base):
    __tablename__ = "guia_costo_detalle_proceso"

    id_detalle_proceso = Column(Integer, primary_key=True, index=True)
    id_guia_costo_servicio = Column(
        Integer,
        ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
        nullable=False,
    )
    # Entrada a cepillado / proceso
    origen_entrada = Column(String(100), nullable=True)
    estado_entrada = Column(String(100), nullable=True)
    planta_secado = Column(String(100), nullable=True)
    planta_cepillado = Column(String(100), nullable=True)
    oc_compra_entrada = Column(String(100), nullable=True)
    espesor_entrada = Column(Numeric(8, 2), nullable=True)
    ancho_entrada = Column(Numeric(8, 2), nullable=True)
    largo_entrada = Column(Numeric(8, 2), nullable=True)
    piezas_entrada = Column(Integer, nullable=True)
    volumen_m3_entrada = Column(Numeric(12, 4), nullable=True)

    # Salida a trozado / proceso
    espesor_salida = Column(Numeric(8, 2), nullable=True)
    ancho_salida = Column(Numeric(8, 2), nullable=True)
    largo_salida = Column(Numeric(8, 2), nullable=True)
    piezas_salida = Column(Integer, nullable=True)
    volumen_m3_salida = Column(Numeric(12, 4), nullable=True)
    proceso = Column(String(100), nullable=True)

    guia_costo = relationship("GuiaCostoServicio", back_populates="detalles_proceso")

    def to_dict(self):
        return {
            "id_detalle_proceso": self.id_detalle_proceso,
            "id_guia_costo_servicio": self.id_guia_costo_servicio,
            "origen_entrada": self.origen_entrada,
            "estado_entrada": self.estado_entrada,
            "planta_secado": self.planta_secado,
            "planta_cepillado": self.planta_cepillado,
            "oc_compra_entrada": self.oc_compra_entrada,
            "espesor_entrada": float(self.espesor_entrada) if self.espesor_entrada is not None else None,
            "ancho_entrada": float(self.ancho_entrada) if self.ancho_entrada is not None else None,
            "largo_entrada": float(self.largo_entrada) if self.largo_entrada is not None else None,
            "piezas_entrada": self.piezas_entrada,
            "volumen_m3_entrada": float(self.volumen_m3_entrada) if self.volumen_m3_entrada is not None else None,
            "espesor_salida": float(self.espesor_salida) if self.espesor_salida is not None else None,
            "ancho_salida": float(self.ancho_salida) if self.ancho_salida is not None else None,
            "largo_salida": float(self.largo_salida) if self.largo_salida is not None else None,
            "piezas_salida": self.piezas_salida,
            "volumen_m3_salida": float(self.volumen_m3_salida) if self.volumen_m3_salida is not None else None,
            "proceso": self.proceso,
        }
