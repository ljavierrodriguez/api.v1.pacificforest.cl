from sqlalchemy import Integer, String, event
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy import Column


class Pais(Base):
    __tablename__ = "pais"

    # === columnas (idénticas a Yii) ===
    id_pais = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)

    # === relaciones HAS_MANY ===
    Agentes = relationship(
        "Agente",
        back_populates="Pais",
        cascade=None,
        passive_deletes=False,
    )

    # (opcional) labels estilo Yii
    @staticmethod
    def attribute_labels():
        return {
            "id_pais": "ID",
            "nombre": "Nombre",
        }

    # (opcional) helper simple para respuestas JSON
    def to_dict(self):
        return {
            "id_pais": self.id_pais,
            "nombre": self.nombre,
        }

    def __repr__(self):
        return f"<Pais {self.id_pais} {self.nombre!r}>"


# ==== Hooks para emular beforeValidate() de Yii (upper-case) ====
@event.listens_for(Pais, "before_insert")
def _pais_upper_insert(mapper, connection, target: Pais):
    if target.nombre:
        target.nombre = target.nombre.upper()


@event.listens_for(Pais, "before_update")
def _pais_upper_update(mapper, connection, target: Pais):
    if target.nombre:
        target.nombre = target.nombre.upper()
