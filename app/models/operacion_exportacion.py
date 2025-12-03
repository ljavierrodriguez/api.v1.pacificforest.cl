from datetime import datetime, date
import sqlalchemy as sa
from sqlalchemy import Integer, String, Date, ForeignKey, func, event, Column
from sqlalchemy.orm import relationship, foreign, object_session
from app.db.base import Base
from app.models.proforma import Proforma 
from app.models.direccion import Direccion
from app.models.contacto_proforma import ContactoProforma
from app.models.cliente_proveedor import ClienteProveedor

# (si tienes Puerto, FormaPago, EstadoOe, también puedes importarlos para back_populates)

def _to_date(v):
    if v is None or isinstance(v, date):
        return v
    s = str(v).strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y%m%d", "%d%m%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


class OperacionExportacion(Base):
    __tablename__ = "operacion_exportacion"

    # En Yii el id lo calculas manualmente → aquí SIN autoincremento
    id_operacion_exportacion = Column(Integer, primary_key=True, autoincrement=False)

    facturar_a        = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    consignar_a       = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    notificar_a       = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    id_puerto_origen  = Column(Integer, ForeignKey("puerto.id_puerto"), nullable=False)
    id_puerto_destino = Column(Integer, ForeignKey("puerto.id_puerto"), nullable=False)

    id_forma_pago = Column(Integer, ForeignKey("forma_pago.id_forma_pago"), nullable=False)

    id_estado_oe = Column(Integer, ForeignKey("estado_oe.id_estado_oe"), nullable=False)
    

    # En la BD es DATE (en Yii haces fecha::varchar en search)
    fecha = Column(Date, nullable=False)

    # ===== Relaciones (nombres como en Yii) =====
    PuertoOrigen = relationship(
        "Puerto",
        back_populates="OperacionOrigen",
        foreign_keys=[id_puerto_origen],
    )
    PuertoDestino = relationship(
        "Puerto",
        back_populates="OperacionDestino",
        foreign_keys=[id_puerto_destino],
    )
    FormaPago = relationship(
        "FormaPago",
        back_populates="OperacionExportaciones",
        foreign_keys=[id_forma_pago],
    )


    EstadoOe = relationship(
        "EstadoOe",
        back_populates="OperacionExportaciones",
        foreign_keys=[id_estado_oe],
    )

    FacturarA  = relationship("ClienteProveedor",
        primaryjoin="foreign(OperacionExportacion.facturar_a)==ClienteProveedor.id_cliente_proveedor",
        viewonly=True)
    ConsignarA = relationship("ClienteProveedor",
        primaryjoin="foreign(OperacionExportacion.consignar_a)==ClienteProveedor.id_cliente_proveedor",
        viewonly=True)
    NotificarA = relationship("ClienteProveedor",
        primaryjoin="foreign(OperacionExportacion.notificar_a)==ClienteProveedor.id_cliente_proveedor",
        viewonly=True)

    # HAS_ONE Proforma (FK está en proforma.id_operacion_exportacion)
    Proforma = relationship(
        "Proforma",
        primaryjoin="OperacionExportacion.id_operacion_exportacion==foreign(Proforma.id_operacion_exportacion)",
        uselist=False,
        back_populates="OperacionExportacion",   # define el inverso en Proforma
    )

    

    def __repr__(self):
        return f"<OperacionExportacion {self.id_operacion_exportacion}>"

    def to_dict(self):
        return {
            "id_operacion_exportacion": self.id_operacion_exportacion,
            "facturar_a": self.facturar_a,
            "consignar_a": self.consignar_a,
            "notificar_a": self.notificar_a,
            "id_puerto_origen": self.id_puerto_origen,
            "id_puerto_destino": self.id_puerto_destino,
            "id_forma_pago": self.id_forma_pago,
            "id_estado_oe": self.id_estado_oe,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }


# ================= Hooks (equivalentes a Yii) =================

@event.listens_for(OperacionExportacion, "before_insert")
def _oe_before_insert(mapper, connection, target: OperacionExportacion):
    """
    Yii::beforeValidate:
      - si id es null => MAX(id)+1
      - mínimo 4136
    """
    if not target.id_operacion_exportacion:
        next_id = connection.execute(
            sa.select(sa.func.coalesce(sa.func.max(OperacionExportacion.id_operacion_exportacion), 0) + 1)
        ).scalar_one()
        if next_id < 4136:
            next_id = 4136
        target.id_operacion_exportacion = next_id

    target.fecha = _to_date(target.fecha)


@event.listens_for(OperacionExportacion, "before_update")
def _oe_before_update(mapper, connection, target: OperacionExportacion):
    """
    Yii::beforeSave (cuando no es nuevo):
      - Si cambian facturar/consignar/notificar y existe Proforma:
        * borrar ContactoProforma del Proforma
        * poner direcciones por defecto (por_defecto=TRUE) en Proforma
    """
    sess = object_session(target)
    if not sess:
        return

    old = sess.get(OperacionExportacion, target.id_operacion_exportacion)
    if not old:
        return

    target.fecha = _to_date(target.fecha)

    proforma = sess.query(Proforma).filter_by(
        id_operacion_exportacion=target.id_operacion_exportacion
    ).one_or_none()
    if not proforma:
        return

    # Helper: id_direccion por defecto de un cliente
    def _dir_defecto(cliente_id: int):
        if not cliente_id:
            return None
        return sess.query(Direccion.id_direccion).filter_by(
            id_cliente_proveedor=cliente_id,
            por_defecto=True
        ).order_by(Direccion.id_direccion).limit(1).scalar()

    # Si cambia facturar_a → borrar contactos del proforma y actualizar dir por defecto
    if old.facturar_a != target.facturar_a:
        sess.query(ContactoProforma).filter_by(id_proforma=proforma.id_proforma).delete(synchronize_session=False)
        dir_id = _dir_defecto(target.facturar_a)
        if dir_id:
            proforma.id_direccion_facturar = dir_id

    # consignar_a
    if old.consignar_a != target.consignar_a:
        dir_id = _dir_defecto(target.consignar_a)
        if dir_id:
            proforma.id_direccion_consignar = dir_id

    # notificar_a
    if old.notificar_a != target.notificar_a:
        dir_id = _dir_defecto(target.notificar_a)
        if dir_id:
            proforma.id_direccion_notificar = dir_id
