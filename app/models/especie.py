from sqlalchemy import Integer, String, Boolean, event, update as sa_update, Column
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base


class Especie(Base):
    __tablename__ = "especie"

    id_especie = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre_esp = Column(String(100), nullable=False)
    nombre_ing = Column(String(100), nullable=False)
    descripcion = Column(String(200))
    por_defecto = Column(Boolean, default=False)
    url_imagen = Column(String(100))

    Productos = relationship(
        "Producto",
        primaryjoin="foreign(Producto.id_especie)==Especie.id_especie",
        lazy="dynamic",
        back_populates="especie",
    )

    def __repr__(self):
        return f"<Especie {self.id_especie} {self.nombre_esp!r}>"

    def to_dict(self):
        return {
            "id_especie": self.id_especie,
            "nombre_esp": self.nombre_esp,
            "nombre_ing": self.nombre_ing,
            "descripcion": self.descripcion,
            "por_defecto": bool(self.por_defecto),
            "url_imagen": self.url_imagen,
        }


# Hooks: uppercase names and ensure single por_defecto
@event.listens_for(Especie, "before_insert")
@event.listens_for(Especie, "before_update")
def _before_save_especie(mapper, connection, target: Especie):
    if target.nombre_esp:
        target.nombre_esp = target.nombre_esp.upper()
    if target.nombre_ing:
        target.nombre_ing = target.nombre_ing.upper()

    if target.por_defecto:
        stmt = (
            sa_update(Especie.__table__)
            .where(Especie.__table__.c.por_defecto == True)
            .where(Especie.__table__.c.id_especie != (target.id_especie or 0))
            .values(por_defecto=False)
        )
        connection.execute(stmt)
