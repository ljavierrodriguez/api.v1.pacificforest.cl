from sqlalchemy import String, Integer, Boolean, event, Column
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.orden_compra import OrdenCompra


class ClienteProveedor(Base):
    __tablename__ = "cliente_proveedor"

    id_cliente_proveedor = Column(Integer, primary_key=True, autoincrement=True, index=True)
    rut = Column(String(15))
    nombre_fantasia = Column(String(200), nullable=False)
    razon_social = Column(String(200), nullable=False)
    es_nacional = Column(Boolean, nullable=False)
    giro = Column(String(200))
    es_cliente = Column(Boolean, nullable=False)
    es_proveedor = Column(Boolean, nullable=False)

    # === Relaciones (nombres iguales a Yii) ===
    Contactos = relationship(
        "Contacto",
        back_populates="ClienteProveedor",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )
    Direcciones = relationship(
        "Direccion",
        back_populates="ClienteProveedor",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )

    Ides = relationship(
        "Ide",
        primaryjoin="ClienteProveedor.id_cliente_proveedor==Ide.id_cliente_notificar_tambien",
        lazy="dynamic",
    )
    Ides1 = relationship(
        "Ide",
        primaryjoin="ClienteProveedor.id_cliente_proveedor==Ide.id_cliente_notificar_a",
        lazy="dynamic",
    )
    Ides2 = relationship(
        "Ide",
        primaryjoin="ClienteProveedor.id_cliente_proveedor==Ide.id_cliente_consignar_a",
        lazy="dynamic",
    )

    OperacionesFacturar = relationship(
        "OperacionExportacion",
        primaryjoin="ClienteProveedor.id_cliente_proveedor==OperacionExportacion.facturar_a",
        lazy="dynamic",
    )
    OperacionesConsignar = relationship(
        "OperacionExportacion",
        primaryjoin="ClienteProveedor.id_cliente_proveedor==OperacionExportacion.consignar_a",
        lazy="dynamic",
    )
    OperacionesNotificar = relationship(
        "OperacionExportacion",
        primaryjoin="ClienteProveedor.id_cliente_proveedor==OperacionExportacion.notificar_a",
        lazy="dynamic",
    )

    OrdenesCompra = relationship(
        "OrdenCompra",
        back_populates="ClienteProveedor",
        lazy="dynamic",
        foreign_keys="OrdenCompra.id_cliente_proveedor",
    )

    def __repr__(self):
        return f"<ClienteProveedor {self.id_cliente_proveedor} {self.razon_social!r}>"


# Trim strings on insert/update
@event.listens_for(ClienteProveedor, "before_insert")
@event.listens_for(ClienteProveedor, "before_update")
def _trim_strings(mapper, connection, target: "ClienteProveedor"):
    def _t(x):
        return x.strip() if isinstance(x, str) else x

    target.razon_social = _t(target.razon_social)
    target.nombre_fantasia = _t(target.nombre_fantasia)
    target.giro = _t(target.giro)
