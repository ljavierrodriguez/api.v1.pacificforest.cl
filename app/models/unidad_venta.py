from sqlalchemy import Integer, String, Boolean, event, Column
from app.db.base import Base
from sqlalchemy.orm import relationship, Session as ORMSession



class UnidadVenta(Base):
    __tablename__ = "unidad_venta"

    id_unidad_venta = Column(Integer, primary_key=True, autoincrement=True)
    nombre          = Column(String(20),  nullable=False, unique=True)
    cubicacion      = Column(String(200), nullable=False)
    descripcion     = Column(String(200), nullable=False)
    por_defecto     = Column(Boolean, default=False)

    # ===== Relaciones (mismos nombres que en Yii) =====
    DetalleOrdenCompra = relationship(
        "DetalleOrdenCompra",
        lazy="dynamic",
        cascade=None,
        back_populates="UnidadVenta",
        foreign_keys="DetalleOrdenCompra.id_unidad_venta",
    )

    """
    DetalleIDE = relationship(
        "DetalleIde",
        lazy="dynamic",
        cascade=None,
        back_populates="UnidadVenta",
        foreign_keys="DetalleIde.id_unidad_venta",
    )
    """
    DetalleProforma = relationship(
        "DetalleProforma",
        lazy="dynamic",
        cascade=None,
        back_populates="UnidadVenta",
        foreign_keys="DetalleProforma.id_unidad_venta",
    )
    DetallePl = relationship(
        "DetallePl",
        lazy="dynamic",
        cascade=None,
        back_populates="UnidadVenta",
        foreign_keys="DetallePl.id_unidad_venta",
    )

    def to_dict(self):
        return {
            "id_unidad_venta": self.id_unidad_venta,
            "nombre": self.nombre,
            "cubicacion": self.cubicacion,
            "descripcion": self.descripcion,
            "por_defecto": self.por_defecto,
        }

    def __repr__(self):
        return f"<UnidadVenta {self.id_unidad_venta} {self.nombre!r}>"


# === Equivalente a beforeSave(): mantener un único por_defecto = TRUE ===
@event.listens_for(ORMSession, "before_flush")
def _ensure_single_default_unidad_venta(session, flush_context, instances):
    for obj in set(list(session.new) + list(session.dirty)):
        if isinstance(obj, UnidadVenta) and obj.por_defecto:
            session.query(UnidadVenta).filter(
                UnidadVenta.por_defecto.is_(True),
                UnidadVenta.id_unidad_venta != (obj.id_unidad_venta or 0)
            ).update({UnidadVenta.por_defecto: False}, synchronize_session=False)
