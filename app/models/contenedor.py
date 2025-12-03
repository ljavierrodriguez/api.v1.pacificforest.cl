from sqlalchemy import Integer, String, Numeric, event, ForeignKey, Column
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base


class Contenedor(Base):
    __tablename__ = "contenedor"

    id_contenedor = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(50), nullable=False)
    tara = Column(Numeric(12, 3))
    peso_maximo = Column(Numeric(12, 3))

    Proformas = relationship(
        "Proforma",
        primaryjoin="foreign(Proforma.id_contenedor)==Contenedor.id_contenedor",
        lazy="dynamic",
        back_populates="Contenedor",
    )

    def __repr__(self):
        return f"<Contenedor {self.id_contenedor} {self.nombre!r}>"

    def to_dict(self):
        return {
            "id_contenedor": self.id_contenedor,
            "nombre": self.nombre,
            "tara": float(self.tara) if self.tara is not None else None,
            "peso_maximo": float(self.peso_maximo) if self.peso_maximo is not None else None,
        }


# Equivalente a beforeValidate() de Yii: nombre en MAYÚSCULAS
@event.listens_for(Contenedor, "before_insert")
@event.listens_for(Contenedor, "before_update")
def _upper_nombre(mapper, connection, target: Contenedor):
    if target.nombre:
        target.nombre = target.nombre.upper()
