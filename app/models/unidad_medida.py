from sqlalchemy import Integer, String, Boolean, event, Column
from app.db.base import Base
from sqlalchemy.orm import relationship, Session


class UnidadMedida(Base):
    __tablename__ = "unidad_medida"

    id_unidad_medida = Column(Integer, primary_key=True, autoincrement=True)
    nombre           = Column(String(10),  nullable=False, unique=True)
    equivalencia_mm  = Column(String(12),  nullable=False)   # En Yii era string(12)
    descripcion      = Column(String(100), nullable=False)
    por_defecto      = Column(Boolean, default=False)

    # ----- DetalleOrdenCompra -----
    detalleOrdenCompras  = relationship(
        "DetalleOrdenCompra",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetalleOrdenCompra.id_unidad_medida_ancho",
        back_populates="UnidadMedidaAncho",
    )
    detalleOrdenCompras1 = relationship(
        "DetalleOrdenCompra",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetalleOrdenCompra.id_unidad_medida_espesor",
        back_populates="UnidadMedidaEspesor",
    )
    detalleOrdenCompras2 = relationship(
        "DetalleOrdenCompra",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetalleOrdenCompra.id_unidad_medida_largo",
        back_populates="UnidadMedidaLargo",
    )

    # ----- DetalleProforma -----
    detalleProformas  = relationship(
        "DetalleProforma",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetalleProforma.id_unidad_medida_ancho",
        back_populates="UnidadMedidaAncho",
    )
    detalleProformas1 = relationship(
        "DetalleProforma",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetalleProforma.id_unidad_medida_espesor",
        back_populates="UnidadMedidaEspesor",
    )
    detalleProformas2 = relationship(
        "DetalleProforma",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetalleProforma.id_unidad_medida_largo",
        back_populates="UnidadMedidaLargo",
    )

    # ----- DetallePl (PLE) -----
    detallePls_ancho_ple = relationship(
        "DetallePl",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetallePl.id_unidad_medida_ancho_ple",
        back_populates="UnidadMedidaAnchoPle",
    )
    detallePls_espesor_ple = relationship(
        "DetallePl",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetallePl.id_unidad_medida_espesor_ple",
        back_populates="UnidadMedidaEspesorPle",
    )
    detallePls_largo_ple = relationship(
        "DetallePl",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetallePl.id_unidad_medida_largo_ple",
        back_populates="UnidadMedidaLargoPle",
    )

    # ----- DetallePl (PLC) -----
    detallePls_ancho_plc = relationship(
        "DetallePl",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetallePl.id_unidad_medida_ancho_plc",
        back_populates="UnidadMedidaAnchoPlc",
    )
    detallePls_espesor_plc = relationship(
        "DetallePl",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetallePl.id_unidad_medida_espesor_plc",
        back_populates="UnidadMedidaEspesorPlc",
    )
    detallePls_largo_plc = relationship(
        "DetallePl",
        lazy="dynamic",
        cascade=None,
        foreign_keys="DetallePl.id_unidad_medida_largo_plc",
        back_populates="UnidadMedidaLargoPlc",
    )

    # ============================================================

    def to_dict(self):
        return {
            "id_unidad_medida": self.id_unidad_medida,
            "nombre": self.nombre,
            "equivalencia_mm": self.equivalencia_mm,
            "descripcion": self.descripcion,
            "por_defecto": self.por_defecto,
        }

    def __repr__(self):
        return f"<UnidadMedida {self.id_unidad_medida} {self.nombre!r}>"


# === Equivalente a beforeSave() de Yii: mantener un único por_defecto = TRUE ===
@event.listens_for(Session, "before_flush")
def _ensure_single_default_unidad_medida(session, flush_context, instances):
    """
    Si se marca una UnidadMedida como por_defecto=True,
    se asegura que todas las demás queden en False.
    """
    for obj in set(list(session.new) + list(session.dirty)):
        if isinstance(obj, UnidadMedida) and obj.por_defecto:
            session.query(UnidadMedida).filter(
                UnidadMedida.por_defecto.is_(True),
                UnidadMedida.id_unidad_medida != (obj.id_unidad_medida or 0)
            ).update({UnidadMedida.por_defecto: False}, synchronize_session=False)
