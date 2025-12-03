# src/models/tipo_comision.py
from sqlalchemy import Integer, String, Boolean, Column
from sqlalchemy.orm import relationship
from sqlalchemy import event
from app.db.base import Base
from sqlalchemy.orm import Session

class TipoComision(Base):
    __tablename__ = "tipo_comision"

    id_tipo_comision = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(20), nullable=False, unique=True)
    por_defecto = Column(Boolean, default=False)

    # Relación HAS_MANY con Proforma (si tienes ese modelo)
    # En Proforma deberías tener: TipoComision = relationship("TipoComision", back_populates="Proformas")
    Proformas = relationship(
        "Proforma",
        back_populates="TipoComision",
        lazy="dynamic",
        cascade=None
    )

    def to_dict(self):
        return {
            "id_tipo_comision": self.id_tipo_comision,
            "nombre": self.nombre,
            "por_defecto": self.por_defecto,
        }

    def __repr__(self):
        return f"<TipoComision {self.id_tipo_comision} {self.nombre!r}>"

# --- Equivalente a beforeSave() de Yii: mantener un único por_defecto = TRUE ---
@event.listens_for(Session, "before_flush")
def _ensure_single_default(session, flush_context, instances):
    """
    Si algún TipoComision que se va a insertar/actualizar viene con por_defecto=True,
    poner por_defecto=False en todos los demás (igual que el beforeSave() de Yii).
    """
    for obj in set(list(session.new) + list(session.dirty)):
        if isinstance(obj, TipoComision) and obj.por_defecto:
            session.query(TipoComision).filter(
                TipoComision.por_defecto.is_(True),
                TipoComision.id_tipo_comision != (obj.id_tipo_comision or 0)
            ).update({TipoComision.por_defecto: False}, synchronize_session=False)
