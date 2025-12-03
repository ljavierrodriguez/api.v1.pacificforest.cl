from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import relationship
from app.db.base import Base


class Contacto(Base):
    __tablename__ = "contacto"

    id_contacto = Column(Integer, primary_key=True, autoincrement=True, index=True)

    nombre = Column(String(100), nullable=False)
    correo = Column(String(100))
    telefono = Column(String(50))

    id_cliente_proveedor = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor", ondelete=None), nullable=False)

    ClienteProveedor = relationship("ClienteProveedor", back_populates="Contactos")

    ContactoOrdenesCompra = relationship(
        "ContactoOrdenCompra",
        back_populates="Contacto",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    ContactosProforma = relationship(
        "ContactoProforma",
        back_populates="Contacto",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    def to_dict(self):
        return {
            "id_contacto": self.id_contacto,
            "nombre": self.nombre,
            "correo": self.correo,
            "telefono": self.telefono,
            "id_cliente_proveedor": self.id_cliente_proveedor,
        }

    def __repr__(self):
        return f"<Contacto {self.id_contacto} {self.nombre!r}>"
