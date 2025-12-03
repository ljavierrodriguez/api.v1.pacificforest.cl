from sqlalchemy import Integer, String, Boolean, ForeignKey, Column
from sqlalchemy.orm import relationship, foreign, backref
from app.db.base import Base


class Direccion(Base):
    __tablename__ = "direccion"

    id_direccion = Column(Integer, primary_key=True, autoincrement=True, index=True)

    direccion = Column(String(200), nullable=False)
    id_ciudad = Column(Integer, ForeignKey("ciudad.id_ciudad"), nullable=False)
    continente = Column(String(15))
    fono_1 = Column(String(15))
    fono_2 = Column(String(15))
    id_cliente_proveedor = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor", ondelete=None), nullable=False)
    por_defecto = Column(Boolean, nullable=False)

    Ciudad = relationship("Ciudad", foreign_keys=[id_ciudad], backref=backref("Direcciones", lazy="dynamic"))
    ClienteProveedor = relationship("ClienteProveedor", back_populates="Direcciones", foreign_keys=[id_cliente_proveedor])

    proformas_consignar = relationship(
        "Proforma",
        primaryjoin="Direccion.id_direccion == foreign(Proforma.id_direccion_consignar)",
        back_populates="DireccionConsignar",
        lazy="dynamic",
    )

    proformas_facturar = relationship(
        "Proforma",
        primaryjoin="Direccion.id_direccion == foreign(Proforma.id_direccion_facturar)",
        back_populates="DireccionFacturar",
        lazy="dynamic",
    )

    proformas_notificar = relationship(
        "Proforma",
        primaryjoin="Direccion.id_direccion == foreign(Proforma.id_direccion_notificar)",
        back_populates="DireccionNotificar",
        lazy="dynamic",
    )

    def to_dict(self):
        return {
            "id_direccion": self.id_direccion,
            "direccion": self.direccion,
            "id_ciudad": self.id_ciudad,
            "continente": self.continente,
            "fono_1": self.fono_1,
            "fono_2": self.fono_2,
            "id_cliente_proveedor": self.id_cliente_proveedor,
            "por_defecto": self.por_defecto,
        }

    def __repr__(self):
        return f"<Direccion {self.id_direccion} {self.direccion!r}>"
