from app.db.base import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import event, Integer, String, Column

class Naviera(Base):
    __tablename__ = "naviera"

    id_naviera = Column(Integer, primary_key=True, autoincrement=True)
    nombre     = Column(String(100), nullable=False, unique=True)

    # HAS_MANY Ide.id_naviera  → crea en Ide la inversa "Naviera"
    Ides = relationship(
        "Ide",
        backref=backref("Naviera"),
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<Naviera {self.id_naviera} {self.nombre}>"

# ===== Normaliza nombre (trim + upper) como tu beforeValidate =====
@event.listens_for(Naviera, "before_insert")
@event.listens_for(Naviera, "before_update")
def _normalize_nombre(mapper, connection, target: Naviera):
    if target.nombre is not None:
        target.nombre = target.nombre.strip().upper()

# ===== Evita borrar si tiene IDEs asociados (como tu beforeDelete) =====
@event.listens_for(Naviera, "before_delete")
def _prevent_delete_if_ides(mapper, connection, target: Naviera):
    # .count() funciona porque Ides es lazy="dynamic"
    if target.Ides.count() > 0:
        # Puedes lanzar ValueError o una excepción propia de tu dominio
        raise ValueError("Existen IDE asociados; no se puede eliminar la naviera.")
