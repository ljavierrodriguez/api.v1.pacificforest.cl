from datetime import date
from sqlalchemy import event, func
from sqlalchemy import Numeric
from sqlalchemy import Integer, String, Date, ForeignKey, Column
from sqlalchemy.orm import relationship, backref
from app.db.base import Base
from sqlalchemy import select

class Proforma(Base):
    __tablename__ = "proforma"

    id_proforma              = Column(Integer, primary_key=True, autoincrement=False)
    id_operacion_exportacion = Column(Integer, ForeignKey("operacion_exportacion.id_operacion_exportacion"))
    id_contenedor            = Column(Integer, ForeignKey("contenedor.id_contenedor"))
    id_usuario_encargado     = Column(Integer, ForeignKey("usuario.id_usuario"))
    id_estado_proforma       = Column(Integer, ForeignKey("estado_proforma.id_estado_proforma"))
    id_moneda                = Column(Integer, ForeignKey("moneda.id_moneda"))
    id_agente                = Column(Integer, ForeignKey("agente.id_agente"))
    id_tipo_comision         = Column(Integer, ForeignKey("tipo_comision.id_tipo_comision"))
    id_clausula_venta        = Column(String(10), ForeignKey("clausula_venta.id_clausula_venta"))
    id_forma_pago            = Column(Integer, ForeignKey("forma_pago.id_forma_pago"))
    cantidad_contenedor      = Column(Integer)
    fecha_emision            = Column(Date, nullable=False)
    fecha_aceptacion         = Column(Date)
    fecha_entrega            = Column(Date)
    valor_flete              = Column(Numeric)  # numeric puro (como en el dump)
    especificaciones         = Column(String(2000))
    nota                     = Column(String(2000))
    nota_1                   = Column(String(2000))
    nota_2                   = Column(String(2000))
    url_imagen               = Column(String(100))
    id_empresa               = Column(Integer, ForeignKey("empresa.id_empresa"), nullable=False)
    id_direccion_facturar    = Column(Integer, ForeignKey("direccion.id_direccion"), nullable=False)
    id_direccion_consignar   = Column(Integer, ForeignKey("direccion.id_direccion"), nullable=False)
    id_direccion_notificar   = Column(Integer, ForeignKey("direccion.id_direccion"), nullable=False)

    #Relaciones
    ContactosProforma = relationship(
        "ContactoProforma",
        back_populates="Proforma",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )
    DetalleProforma = relationship(
        "DetalleProforma",
        back_populates="Proforma",
        lazy="dynamic",
        cascade=None,
        passive_deletes=False,
    )
    OrdenesCompra = relationship(                    # HAS_MANY ordenes actuales
        "OrdenCompra",
        back_populates="Proforma",
        lazy="dynamic",
        primaryjoin="Proforma.id_proforma==foreign(OrdenCompra.id_proforma)",
    )
    OrdenesCompraAnterior = relationship(            # HAS_MANY ordenes donde esta proforma fue 'anterior'
        "OrdenCompra",
        back_populates="ProformaAnterior",
        lazy="dynamic",
        primaryjoin="Proforma.id_proforma==foreign(OrdenCompra.id_proforma_anterior)",
    )

    # BELONGS_TO
    DireccionConsignar = relationship(
        "Direccion",
        back_populates="proformas_consignar",
        foreign_keys=[id_direccion_consignar],
    )
    DireccionFacturar = relationship(
        "Direccion",
        back_populates="proformas_facturar",
        foreign_keys=[id_direccion_facturar],
    )
    DireccionNotificar = relationship(
        "Direccion",
        back_populates="proformas_notificar",
        foreign_keys=[id_direccion_notificar],
    )
    Agente = relationship("Agente", back_populates="proformas")
    ClausulaVenta = relationship("ClausulaVenta", back_populates="Proformas")
    Contenedor = relationship("Contenedor", back_populates="Proformas")
    EstadoProforma = relationship("EstadoProforma", back_populates="Proformas")
    FormaPago = relationship("FormaPago", foreign_keys=[id_forma_pago])
  
    OperacionExportacion = relationship(
        "OperacionExportacion",
        back_populates="Proforma",          # en OE define Proforma = relationship(..., uselist=False)
        foreign_keys=[id_operacion_exportacion],
    )
    TipoComision = relationship("TipoComision", back_populates="Proformas")
    UsuarioEncargado = relationship(
    "User",
    foreign_keys=[id_usuario_encargado], 
    backref=backref(
        "ProformasEncargado",   
        lazy="dynamic"          
    )
    )
    
    Empresa = relationship(
    "Empresa",
    foreign_keys=[id_empresa],       
    backref=backref(
        "Proformas",                 
        lazy="dynamic"              
    )
    )

    # --- utilidades ---
    def serialize(self) -> dict:
        to_str = lambda d: d.isoformat() if isinstance(d, date) and d else None
        return {
            "id_proforma": self.id_proforma,
            "id_operacion_exportacion": self.id_operacion_exportacion,
            "id_contenedor": self.id_contenedor,
            "id_usuario_encargado": self.id_usuario_encargado,
            "id_estado_proforma": self.id_estado_proforma,
            "id_moneda": self.id_moneda,
            "id_agente": self.id_agente,
            "id_tipo_comision": self.id_tipo_comision,
            "id_clausula_venta": self.id_clausula_venta,
            "id_forma_pago": self.id_forma_pago,
            "cantidad_contenedor": self.cantidad_contenedor,
            "fecha_emision": to_str(self.fecha_emision),
            "fecha_aceptacion": to_str(self.fecha_aceptacion),
            "fecha_entrega": to_str(self.fecha_entrega),
            "valor_flete": str(self.valor_flete) if self.valor_flete is not None else None,
            "especificaciones": self.especificaciones,
            "nota": self.nota,
            "nota_1": self.nota_1,
            "nota_2": self.nota_2,
            "url_imagen": self.url_imagen,
            "id_empresa": self.id_empresa,
            "id_direccion_facturar": self.id_direccion_facturar,
            "id_direccion_consignar": self.id_direccion_consignar,
            "id_direccion_notificar": self.id_direccion_notificar,
        }

# (opcional) emula el beforeSave de Yii para id_proforma = max+1 (con mínimo 1798)
@event.listens_for(Proforma, "before_insert")
def proforma_before_insert(mapper, connection, target):
    if target.id_proforma is None:
        max_id = connection.execute(select(func.coalesce(func.max(Proforma.id_proforma), 0))).scalar_one()
        target.id_proforma = max(max_id + 1, 1798)
