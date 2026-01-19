# src/models/producto.py
from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class Producto(Base):
    __tablename__ = "producto"

    # PK
    id_producto = Column(Integer, primary_key=True, autoincrement=True)

    # FKs (opcionales porque en Yii no son required)
    id_clase   = Column(Integer, ForeignKey("clase.id_clase", ondelete=None), nullable=True)
    id_especie = Column(Integer, ForeignKey("especie.id_especie", ondelete=None), nullable=True)

    # Campos (mismos tamaños y required que en rules() de Yii)
    nombre_producto_esp = Column(String(100), nullable=False)  # required
    nombre_producto_ing = Column(String(100), nullable=False)  # required
    obs_calidad         = Column(String(2000))                 # optional

    # ===== Relaciones (mismos nombres que en Yii) =====
    # BELONGS_TO
    clase   = relationship("Clase", back_populates="Productos")
    especie = relationship("Especie", back_populates="Productos")

    # HAS_MANY
    DetalleOrdenCompras = relationship(
        "DetalleOrdenCompra",
        back_populates="Producto",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )
    DetalleProforma = relationship(
        "DetalleProforma",
        back_populates="Producto",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    # --- utilidades opcionales ---
    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "id_clase": self.id_clase,
            "id_especie": self.id_especie,
            "nombre_producto_esp": self.nombre_producto_esp,
            "nombre_producto_ing": self.nombre_producto_ing,
            "obs_calidad": self.obs_calidad,
        }

    def __repr__(self):
        return f"<Producto {self.id_producto} {self.nombre_producto_esp!r}>"
