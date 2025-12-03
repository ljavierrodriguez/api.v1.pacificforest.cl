from sqlalchemy import event, update, Integer, String, Boolean, Column
from app.db.base import Base
from sqlalchemy.orm import relationship

class Moneda(Base):
    __tablename__ = "moneda"

    id_moneda     = Column(Integer, primary_key=True)
    etiqueta      = Column(String(10), nullable=False, unique=True)
    nombre_moneda = Column(String(200))
    por_defecto   = Column(Boolean, default=False)

    # Relaciones (mismo naming que en Yii)
    Proformas      = relationship("Proforma", backref="Moneda", lazy="dynamic")
    OrdenesCompra  = relationship("OrdenCompra", backref="Moneda", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Moneda id={self.id_moneda} etiqueta={self.etiqueta}>"

    def serialize(self) -> dict:
        return {
            "id_moneda": self.id_moneda,
            "etiqueta": self.etiqueta,
            "nombre_moneda": self.nombre_moneda,
            "por_defecto": self.por_defecto,  # sin cast: queda 1:1 con Yii
        }


# ====== Emular Yii::beforeSave() para 'por_defecto' ======
@event.listens_for(Moneda, "before_insert")
@event.listens_for(Moneda, "before_update")
def _solo_una_por_defecto(mapper, connection, target: Moneda):
    if target.por_defecto:
        connection.execute(
            update(Moneda.__table__)
            .where(Moneda.__table__.c.por_defecto.is_(True))
            .where(Moneda.__table__.c.id_moneda != (target.id_moneda or -1))
            .values(por_defecto=False)
        )
