
from sqlalchemy.orm import relationship, backref
from sqlalchemy import event, Column, Integer, String
from app.db.base import Base

class TipoEnvase(Base):
    __tablename__ = "tipo_envase"

    id_tipo_envase = Column(Integer, primary_key=True, autoincrement=True)
    nombre         = Column(String(50), nullable=False, unique=True)

    # HAS_MANY Ide.id_tipo_envase  → crea en Ide la inversa "TipoEnvase"
    Ides = relationship(
        "Ide",
        backref=backref("TipoEnvase"),
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<TipoEnvase {self.id_tipo_envase} {self.nombre}>"

# === Normaliza nombre (trim + upper) como en beforeValidate de Yii ===
@event.listens_for(TipoEnvase, "before_insert")
@event.listens_for(TipoEnvase, "before_update")
def _normalize_nombre(mapper, connection, target: TipoEnvase):
    if target.nombre is not None:
        target.nombre = target.nombre.strip().upper()

# === Evita borrar si tiene IDEs asociados (como beforeDelete) ===
@event.listens_for(TipoEnvase, "before_delete")
def _prevent_delete_if_ides(mapper, connection, target: TipoEnvase):
    # .count() funciona porque Ides es lazy="dynamic"
    if target.Ides.count() > 0:
        raise ValueError("Existen IDE asociados; no se puede eliminar el tipo de envase.")
