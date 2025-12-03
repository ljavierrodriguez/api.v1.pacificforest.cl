from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import event, func, select, text, Integer, String, Date, Boolean, Numeric, ForeignKey, Column
from sqlalchemy.orm import validates, relationship, backref
from app.db.base import Base


def _to_date_or_none(v):
    if v in (None, "", "null"):
        return None
    if isinstance(v, date):
        return v
    # Acepta 'YYYY-MM-DD' (lo más común en tu app)
    try:
        return datetime.strptime(v, "%Y-%m-%d").date()
    except Exception:
        # intenta dd/mm/yyyy por si viene así de la UI
        try:
            return datetime.strptime(v, "%d/%m/%Y").date()
        except Exception:
            return None


class Ple(Base):
    __tablename__ = "ple"

    id_ple = Column(Integer, primary_key=True)
    id_orden_compra= Column(Integer,ForeignKey("orden_compra.id_orden_compra", ondelete="RESTRICT"),nullable=False,index=True,)
    id_estado_pl = Column(Integer,ForeignKey("estado_pl.id_estado_pl", ondelete="RESTRICT"),index=True,)
    fecha_creacion = Column(Date, nullable=False)
    nro_guia = Column(Integer)
    despacho = Column(Date)
    volumen_m3 = Column(Numeric(12, 3), nullable=False)
    paquetes = Column(Integer, nullable=False)
    piezas   = Column(Integer, nullable=False)
    costo_total_pesos = Column(Numeric(12, 3), nullable=False)
    tc = Column(Numeric(12, 3))
    factura = Column(Integer)
    monto_factura = Column(Numeric(12, 3))
    factura_pagada = Column(Boolean, default=False)
    id_usuario_encargado = Column(Integer,ForeignKey("usuario.id_usuario", ondelete="RESTRICT"),index=True,)

   
    DetallePl = relationship(
        "DetallePl",
        back_populates="Ple",
        cascade="all, delete-orphan",
        lazy="dynamic",
        passive_deletes=True,
    )
    EstadoPl = relationship(
        "EstadoPl",
        back_populates="Ples",
        foreign_keys=[id_estado_pl]
    )
    OrdenCompra = relationship(
        "OrdenCompra",
        back_populates="Ples",
    )
    UsuarioEncargado = relationship(
    "User",
    backref=backref("PlesEncargado", lazy="dynamic"),
    foreign_keys=[id_usuario_encargado],
    )

    # --------------------
    # Validaciones estilo beforeValidate de Yii
    # (se ejecutan en before_insert / before_update)
    # --------------------
    def _validate_business_rules(self):
        # factura_pagada requiere factura
        if self.factura_pagada and self.factura is None:
            raise ValueError("factura no puede ser nulo si factura_pagada es true")

        # si hay factura, monto_factura debe ser > 0
        if self.factura is not None:
            if self.monto_factura is None or Decimal(self.monto_factura) <= 0:
                raise ValueError("monto_factura debe ser mayor que 0 cuando hay factura")

        # paquetes no puede ser 0
        if self.paquetes is None or int(self.paquetes) == 0:
            raise ValueError("Debe indicar la cantidad de paquetes (paquetes > 0)")

    # Normalización básica de fechas si llegan como string
    @validates("fecha_creacion", "despacho")
    def _valida_fechas(self, key, value):
        return _to_date_or_none(value)

    # Serializer opcional
    def serialize(self) -> dict:
        to_str = lambda d: d.isoformat() if isinstance(d, date) and d else None
        to_num = lambda n: float(n) if n is not None else None
        return {
            "id_ple": self.id_ple,
            "id_orden_compra": self.id_orden_compra,
            "id_estado_pl": self.id_estado_pl,
            "fecha_creacion": to_str(self.fecha_creacion),
            "nro_guia": self.nro_guia,
            "despacho": to_str(self.despacho),
            "volumen_m3": to_num(self.volumen_m3),
            "paquetes": self.paquetes,
            "piezas": self.piezas,
            "costo_total_pesos": to_num(self.costo_total_pesos),
            "tc": to_num(self.tc),
            "factura": self.factura,
            "monto_factura": to_num(self.monto_factura),
            "factura_pagada": bool(self.factura_pagada),
            "id_usuario_encargado": self.id_usuario_encargado,
        }

    def __repr__(self) -> str:
        return f"<Ple id={self.id_ple} oc={self.id_orden_compra} fecha={self.fecha_creacion}>"

# -------------------------------------------------
# Hooks que emulan beforeSave / beforeDelete de Yii
# -------------------------------------------------

@event.listens_for(Ple, "before_insert")
def ple_before_insert(mapper, connection, target: Ple):
    # Emula el incremento manual que hacía Yii si id_ple viene en null.
    if target.id_ple is None:
        next_id = connection.execute(
            select(func.coalesce(func.max(Ple.id_ple), 0) + 1)
        ).scalar_one()
        target.id_ple = next_id

    # Normalización de fechas por si llegaron como string
    target.fecha_creacion = _to_date_or_none(target.fecha_creacion)
    target.despacho = _to_date_or_none(target.despacho)

    # Boolean explícito
    target.factura_pagada = bool(target.factura_pagada)

    # Reglas de negocio del beforeValidate
    target._validate_business_rules()


@event.listens_for(Ple, "before_update")
def ple_before_update(mapper, connection, target: Ple):
    target.fecha_creacion = _to_date_or_none(target.fecha_creacion)
    target.despacho = _to_date_or_none(target.despacho)
    target.factura_pagada = bool(target.factura_pagada)
    target._validate_business_rules()


@event.listens_for(Ple, "before_delete")
def ple_before_delete(mapper, connection, target: Ple):
    # Bloquea eliminación si existen detalle_pl con id_plc no nulo (como en Yii)
    detalle_count = connection.execute(
        select(func.count()).select_from(text("detalle_pl")).where(
            text("id_ple = :pid AND id_plc IS NOT NULL")
        ),
        {"pid": target.id_ple},
    ).scalar_one()
    if detalle_count and int(detalle_count) > 0:
        # Lanza excepción (se traduce a 400/409 según lo manejes en tu capa de errores)
        raise ValueError("El detalle tiene Packing List Comex asociado; no es posible eliminar.")
