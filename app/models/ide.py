from datetime import datetime, date
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Date,
    ForeignKey,
    Column,
)
from sqlalchemy.orm import relationship, foreign, backref
from sqlalchemy import event
from app.db.base import Base
from app.models.bodega import Bodega
from app.models.forma_pago import FormaPago
from app.models.tipo_comision import TipoComision

def _to_date(v):
    """Equiv. a Format::DbDate: acepta str y devuelve date; deja None si no matchea."""
    if v is None or isinstance(v, date):
        return v
    s = str(v).strip().replace("/", "-")
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y%m%d", "%d%m%Y"):
        try: return datetime.strptime(s, fmt).date()
        except ValueError: pass
    return None

class Ide(Base):
    __tablename__ = "ide"
    id_ide = Column(Integer, primary_key=True, autoincrement=True)
    id_naviera = Column(Integer, ForeignKey("naviera.id_naviera"), nullable=True)
    id_cliente_consignar_a = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    direccion_consignar_a = Column(String(500), nullable=False)
    id_cliente_notificar_a = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    direccion_notificar_a = Column(String(500), nullable=False)
    id_bodega = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=False)
    id_cliente_notificar_tambien = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"))
    direccion_tambien_notificar = Column(String(500))
    id_tipo_envase = Column(Integer, ForeignKey("tipo_envase.id_tipo_envase"), nullable=False)
    id_usuario_responsable = Column(Integer, nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    fecha_emision = Column(Date, nullable=False)
    nave = Column(String(100), nullable=False)
    comision = Column(String(100))
    retiro_unidades = Column(String(100))
    codigo_reserva = Column(String(100))
    medio_transporte = Column(String(15))
    etd = Column(Date, nullable=False)
    tiempo_transito = Column(Integer, nullable=False)
    eta = Column(Date, nullable=False)
    flete = Column(String(13))
    confirma_zarpe = Column(Boolean)
    fob = Column(String(13))
    stacking = Column(Date)
    seguro_app = Column(String(13))
    total_flete = Column(String(13))
    total = Column(String(13))
    id_cliente_facturar_a = Column(Integer, ForeignKey("cliente_proveedor.id_cliente_proveedor"), nullable=False)
    id_puerto_origen = Column(Integer, nullable=False)
    id_puerto_destino = Column(Integer, nullable=False)
    id_clausula_venta = Column(String(10), ForeignKey("clausula_venta.id_clausula_venta"), nullable=False)
    id_forma_pago = Column(Integer, nullable=False)
    id_tipo_comision = Column(Integer)
    id_moneda = Column(Integer, nullable=False)
    carta_credito = Column(String(60))
    fecha_carta_credito = Column(String(60))
    modalidad_venta = Column(String(100), nullable=False)
    tipo_flete = Column(String(60))

    # === relaciones (nombres como en Yii) ===
    # HAS_MANY
  

    DocumentosIDE = relationship("DocumentoIde", lazy="dynamic", backref=backref("Ide"))

    # BELONGS_TO ClienteProveedor por tres FKs distintos
    ClienteNotificarTambien = relationship(
        "ClienteProveedor",
        primaryjoin="foreign(Ide.id_cliente_notificar_tambien)==ClienteProveedor.id_cliente_proveedor",
        viewonly=True,
    )
    ClienteConsignarA = relationship(
        "ClienteProveedor",
        primaryjoin="foreign(Ide.id_cliente_consignar_a)==ClienteProveedor.id_cliente_proveedor",
        viewonly=True,
    )
    ClienteNotificarA = relationship(
        "ClienteProveedor",
        primaryjoin="foreign(Ide.id_cliente_notificar_a)==ClienteProveedor.id_cliente_proveedor",
        viewonly=True,
    )

    # BELONGS_TO otras entidades (dejamos viewonly; luego agregas back_populates si quieres)
    
   
    UsuarioResponsable = relationship("User",            primaryjoin="foreign(Ide.id_usuario_responsable)==User.id_usuario", viewonly=True)
    ClienteFacturarA   = relationship("ClienteProveedor",   primaryjoin="foreign(Ide.id_cliente_facturar_a)==ClienteProveedor.id_cliente_proveedor", viewonly=True)
    PuertoOrigen       = relationship("Puerto",             primaryjoin="foreign(Ide.id_puerto_origen)==Puerto.id_puerto", viewonly=True)
    PuertoDestino      = relationship("Puerto",             primaryjoin="foreign(Ide.id_puerto_destino)==Puerto.id_puerto", viewonly=True)
    Bodega = relationship("Bodega",back_populates="Ides",foreign_keys=[id_bodega])
    FormaPago          = relationship("FormaPago",          primaryjoin="foreign(Ide.id_forma_pago)==FormaPago.id_forma_pago", viewonly=True)
    ClausulaVenta      = relationship("ClausulaVenta",      primaryjoin="foreign(Ide.id_clausula_venta)==ClausulaVenta.id_clausula_venta", viewonly=True)
    TipoComision       = relationship("TipoComision",       primaryjoin="foreign(Ide.id_tipo_comision)==TipoComision.id_tipo_comision", viewonly=True)
    Moneda             = relationship("Moneda",             primaryjoin="foreign(Ide.id_moneda)==Moneda.id_moneda", viewonly=True)

    # HAS_MANY Factura (en Yii comentas que no es FK real; la usamos sólo para lectura)
    Facturas = relationship("Factura", back_populates="Ide",lazy="dynamic",foreign_keys="Factura.id_ide")

    def __repr__(self):
        return f"<Ide {self.id_ide}>"

    def to_dict(self):
        d = {
            "id_ide": self.id_ide,
            "id_naviera": self.id_naviera,
            "id_cliente_consignar_a": self.id_cliente_consignar_a,
            "direccion_consignar_a": self.direccion_consignar_a,
            "id_cliente_notificar_a": self.id_cliente_notificar_a,
            "direccion_notificar_a": self.direccion_notificar_a,
            "id_cliente_notificar_tambien": self.id_cliente_notificar_tambien,
            "direccion_tambien_notificar": self.direccion_tambien_notificar,
            "id_tipo_envase": self.id_tipo_envase,
            "id_usuario_responsable": self.id_usuario_responsable,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_emision": self.fecha_emision.isoformat() if self.fecha_emision else None,
            "nave": self.nave,
            "comision": self.comision,
            "retiro_unidades": self.retiro_unidades,
            "codigo_reserva": self.codigo_reserva,
            "medio_transporte": self.medio_transporte,
            "etd": self.etd.isoformat() if self.etd else None,
            "tiempo_transito": self.tiempo_transito,
            "eta": self.eta.isoformat() if self.eta else None,
            "flete": self.flete,
            "confirma_zarpe": self.confirma_zarpe,
            "fob": self.fob,
            "stacking": self.stacking.isoformat() if self.stacking else None,
            "seguro_app": self.seguro_app,
            "total_flete": self.total_flete,
            "total": self.total,
            "id_cliente_facturar_a": self.id_cliente_facturar_a,
            "id_puerto_origen": self.id_puerto_origen,
            "id_puerto_destino": self.id_puerto_destino,
            "id_bodega": self.id_bodega,
            "id_clausula_venta": self.id_clausula_venta,
            "id_forma_pago": self.id_forma_pago,
            "id_tipo_comision": self.id_tipo_comision,
            "id_moneda": self.id_moneda,
            "carta_credito": self.carta_credito,
            "fecha_carta_credito": self.fecha_carta_credito,
            "modalidad_venta": self.modalidad_venta,
            "tipo_flete": self.tipo_flete,
        }
        return d

# === Hook estilo beforeSave() de Yii para normalizar fechas ===
@event.listens_for(Ide, "before_insert")
@event.listens_for(Ide, "before_update")
def _normalize_dates(mapper, connection, target: Ide):
    target.fecha_creacion = _to_date(target.fecha_creacion)
    target.fecha_emision  = _to_date(target.fecha_emision)
    target.etd            = _to_date(target.etd)
    target.eta            = _to_date(target.eta)
    target.stacking       = _to_date(target.stacking)
