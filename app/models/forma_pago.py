from sqlalchemy import Integer, String, Boolean, event, Column
from sqlalchemy.orm import relationship
from app.db.base import Base

class FormaPago(Base):
    __tablename__ = "forma_pago"

    id_forma_pago = Column(Integer, primary_key=True, autoincrement=True)
    nombre        = Column(String(50), nullable=False, unique=True)
    por_defecto   = Column(Boolean, default=False)


    OperacionExportaciones = relationship(
        "OperacionExportacion",
        back_populates="FormaPago",
        lazy="dynamic",
        cascade=None,
        foreign_keys="OperacionExportacion.id_forma_pago",
    )

    # (opcional) helper para respuestas JSON simples
    def to_dict(self):
        return {
            "id_forma_pago": self.id_forma_pago,
            "nombre": self.nombre,
            "por_defecto": self.por_defecto,
        }

    def __repr__(self):
        return f"<FormaPago {self.id_forma_pago} {self.nombre!r} por_defecto={self.por_defecto}>"

# ===== Reproduce Yii::beforeSave() =====
# Si se guarda un registro con por_defecto=True, apaga por_defecto en los demás.
@event.listens_for(FormaPago, "before_insert")
@event.listens_for(FormaPago, "before_update")
def _ensure_single_default(mapper, connection, target: FormaPago):
    if target.por_defecto:
        # Equivalente a:
        # FormaPago::model()->updateAll(['por_defecto'=>false], 'por_defecto and id<>:id', [':id'=>...])
        # Aquí apagamos todos; el actual quedará True al persistirse.
        connection.execute(
            FormaPago.__table__.update().values(por_defecto=False)
        )
