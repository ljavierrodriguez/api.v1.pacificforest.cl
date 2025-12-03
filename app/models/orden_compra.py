from datetime import date
from sqlalchemy import (Integer, String, Date, Boolean, Numeric, ForeignKey, event, select, func, Column, text)
from sqlalchemy.orm import relationship, validates
from app.db.base import Base


class OrdenCompra(Base):
    __tablename__ = "orden_compra"

    # ===== Campos =====
    id_orden_compra        = Column(Integer, primary_key=True)   # Yii hace max+1 si es None (ver evento abajo)
    id_proforma            = Column(Integer, ForeignKey("proforma.id_proforma"))
    id_proforma_anterior   = Column(Integer, ForeignKey("proforma.id_proforma"))

    fecha_emision          = Column(Date, nullable=False)
    id_cliente_proveedor   = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    id_usuario_encargado   = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    fecha_entrega          = Column(Date, nullable=False)

    id_bodega              = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=False)
    destino                = Column(String(15))
    id_moneda              = Column(Integer, ForeignKey("moneda.id_moneda"), nullable=False)
    id_empresa             = Column(Integer, ForeignKey("empresa.id_empresa"))

    ajustar_volumen        = Column(Boolean, default=False)  # Yii lo normaliza a 1/0; aquí boolean nativo
    observacion            = Column(String(1000))
    id_usuario             = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    nota_1                 = Column(String(1000))
    otras_especificaciones = Column(String(1000))
    url_imagen             = Column(String(100))

    valor_neto             = Column(Numeric(13, 3), nullable=False)
    iva                    = Column(Numeric(12, 3), nullable=False)
    tasa_iva               = Column(Numeric(6, 3))            # en Yii era length, aquí decimal acorde a redondeo
    valor_total            = Column(Numeric(12, 3), nullable=False)

    id_estado_odc          = Column(Integer, ForeignKey("estado_odc.id_estado_odc"), nullable=False)
    id_direccion_proveedor = Column(Integer, ForeignKey("direccion.id_direccion"), nullable=False)
    vinculado              = Column(Integer)  # mismo tipo que en Yii

    # ===== Relaciones (mismos nombres que en Yii) =====
    ContactosOrdenCompra = relationship(
        "ContactoOrdenCompra",
        back_populates="OrdenCompra",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    DetalleOrdenCompra = relationship(
        "DetalleOrdenCompra",
        back_populates="OrdenCompra",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    Proforma = relationship(
        "Proforma",
        back_populates="OrdenesCompra",
        foreign_keys=[id_proforma],
    )

    ProformaAnterior = relationship(
        "Proforma",
        back_populates="OrdenesCompraAnterior",
        foreign_keys=[id_proforma_anterior],
    )

    ClienteProveedor = relationship(
    "ClienteProveedor",
     back_populates="OrdenesCompra",
    foreign_keys=[id_cliente_proveedor],   # ← evita ambigüedad y asegura el mapeo
    )
   
    Usuario   = relationship("User", foreign_keys=[id_usuario])
    UsuarioEncargado = relationship("User", foreign_keys=[id_usuario_encargado])
    Empresa   = relationship("Empresa")
    EstadoOdc = relationship("EstadoOdc")
    EstadoOdc = relationship("EstadoOdc", back_populates="OrdenesCompra",foreign_keys=[id_estado_odc])
    DireccionProveedor = relationship("Direccion")
    Ples      = relationship("Ple", back_populates="OrdenCompra", lazy="dynamic")

    # ===== Validaciones equivalentes a beforeValidate() de Yii =====
    @validates("fecha_entrega", "fecha_emision")
    def _validate_fechas(self, key, value):
        # Si ambas fechas están presentes, no permitir entrega < emisión
        if key == "fecha_entrega" and value and self.fecha_emision and value < self.fecha_emision:
            raise ValueError("Fecha de entrega no puede ser menor a fecha de emisión")
        return value

    @validates("valor_neto", "valor_total", "iva")
    def _round_montos(self, key, value):
        # Yii redondea a 3 decimales antes de validar
        if value is None:
            return None
        # usar cuantización a 3 decimales
        from decimal import Decimal, ROUND_HALF_UP
        return (Decimal(value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))

    # ===== Helpers opcionales =====
    def serialize(self) -> dict:
        to_str = lambda d: d.isoformat() if isinstance(d, date) and d else None
        as_float = lambda x: float(x) if x is not None else None
        return {
            "id_orden_compra": self.id_orden_compra,
            "id_proforma": self.id_proforma,
            "id_proforma_anterior": self.id_proforma_anterior,
            "fecha_emision": to_str(self.fecha_emision),
            "id_cliente_proveedor": self.id_cliente_proveedor,
            "id_usuario_encargado": self.id_usuario_encargado,
            "fecha_entrega": to_str(self.fecha_entrega),
            "id_bodega": self.id_bodega,
            "destino": self.destino,
            "id_moneda": self.id_moneda,
            "id_empresa": self.id_empresa,
            "ajustar_volumen": bool(self.ajustar_volumen),
            "observacion": self.observacion,
            "id_usuario": self.id_usuario,
            "nota_1": self.nota_1,
            "otras_especificaciones": self.otras_especificaciones,
            "url_imagen": self.url_imagen,
            "valor_neto": as_float(self.valor_neto),
            "iva": as_float(self.iva),
            "tasa_iva": as_float(self.tasa_iva),
            "valor_total": as_float(self.valor_total),
            "id_estado_odc": self.id_estado_odc,
            "id_direccion_proveedor": self.id_direccion_proveedor,
            "vinculado": self.vinculado,
        }

    def __repr__(self) -> str:
        return f"<OrdenCompra id={self.id_orden_compra} proforma={self.id_proforma}>"

# ===== Eventos para emular beforeSave/beforeDelete de Yii =====

# Emular beforeSave: si id_orden_compra es None, asignar max+1 y forzar mínimo 2315
@event.listens_for(OrdenCompra, "before_insert")
def _assign_pk_before_insert(mapper, connection, target: OrdenCompra):
    if target.id_orden_compra is None:
        next_id = connection.execute(
            select(func.coalesce(func.max(OrdenCompra.id_orden_compra), 0) + 1)
        ).scalar_one()
        target.id_orden_compra = max(next_id, 2315)

# Emular antes de borrar: bloquear si existen PLE asociados (y limpiar archivos si quieres replicar eso)
@event.listens_for(OrdenCompra, "before_delete")
def _guard_delete_if_has_ple(mapper, connection, target: OrdenCompra):
    # cuenta PLE asociados
    ple_count = connection.execute(
        select(func.count()).select_from(text("ple")).where(
            text("ple.id_orden_compra = :oid")
        ),
        {"oid": target.id_orden_compra},
    ).scalar_one()
    if ple_count:
        # mismo comportamiento que lanzar CDbException en Yii
        raise ValueError("No es posible eliminar: tiene PLE asociados")
    # En Yii también eliminan el archivo físico; si deseas replicarlo, hazlo en tu capa de servicio.
