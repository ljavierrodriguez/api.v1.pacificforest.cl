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

    # Empresa snapshot fields (immutable historical data)
    empresa_nombre_fantasia  = Column(String(200))
    empresa_razon_social     = Column(String(200))
    empresa_rut              = Column(String(15))
    empresa_direccion        = Column(String(200))
    empresa_giro             = Column(String(200))

    # Billing address snapshot fields (immutable historical data)
    direccion_facturar_texto = Column(String(200))
    direccion_facturar_ciudad = Column(String(100))
    direccion_facturar_pais  = Column(String(100))
    direccion_facturar_fono_1 = Column(String(15))

    # Consignment address snapshot fields (immutable historical data)
    direccion_consignar_texto = Column(String(200))
    direccion_consignar_ciudad = Column(String(100))
    direccion_consignar_pais = Column(String(100))
    direccion_consignar_fono_1 = Column(String(15))

    # Notification address snapshot fields (immutable historical data)
    direccion_notificar_texto = Column(String(200))
    direccion_notificar_ciudad = Column(String(100))
    direccion_notificar_pais = Column(String(100))
    direccion_notificar_fono_1 = Column(String(15))

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
    #FormaPago = relationship("FormaPago", foreign_keys=[id_forma_pago])
  
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
        
        result = {
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
        
        # Add empresa snapshots (with fallback to current Empresa data)
        if self.empresa_nombre_fantasia:
            result["empresa"] = {
                "nombre_fantasia": self.empresa_nombre_fantasia,
                "razon_social": self.empresa_razon_social,
                "rut": self.empresa_rut,
                "direccion": self.empresa_direccion,
                "giro": self.empresa_giro,
            }
        elif self.Empresa and hasattr(self.Empresa, 'nombre_fantasia'):
            # Fallback to current empresa data for backward compatibility
            try:
                result["empresa"] = {
                    "nombre_fantasia": self.Empresa.nombre_fantasia,
                    "razon_social": self.Empresa.razon_social,
                    "rut": self.Empresa.rut,
                    "direccion": self.Empresa.direccion,
                    "giro": self.Empresa.giro,
                }
            except:
                result["empresa"] = None
        else:
            result["empresa"] = None
        
        # Add billing address snapshots (with fallback)
        if self.direccion_facturar_texto:
            result["direccion_facturar"] = {
                "texto": self.direccion_facturar_texto,
                "ciudad": self.direccion_facturar_ciudad,
                "pais": self.direccion_facturar_pais,
                "fono_1": self.direccion_facturar_fono_1,
            }
        elif self.DireccionFacturar and hasattr(self.DireccionFacturar, 'direccion'):
            # Fallback to current direccion data
            try:
                result["direccion_facturar"] = {
                    "texto": self.DireccionFacturar.direccion,
                    "ciudad": self.DireccionFacturar.Ciudad.nombre if self.DireccionFacturar.Ciudad else None,
                    "pais": self.DireccionFacturar.Ciudad.Pais.nombre if self.DireccionFacturar.Ciudad and self.DireccionFacturar.Ciudad.Pais else None,
                    "fono_1": self.DireccionFacturar.fono_1,
                }
            except:
                result["direccion_facturar"] = None
        else:
            result["direccion_facturar"] = None
        
        # Add consignment address snapshots (with fallback)
        if self.direccion_consignar_texto:
            result["direccion_consignar"] = {
                "texto": self.direccion_consignar_texto,
                "ciudad": self.direccion_consignar_ciudad,
                "pais": self.direccion_consignar_pais,
                "fono_1": self.direccion_consignar_fono_1,
            }
        elif self.DireccionConsignar and hasattr(self.DireccionConsignar, 'direccion'):
            # Fallback to current direccion data
            try:
                result["direccion_consignar"] = {
                    "texto": self.DireccionConsignar.direccion,
                    "ciudad": self.DireccionConsignar.Ciudad.nombre if self.DireccionConsignar.Ciudad else None,
                    "pais": self.DireccionConsignar.Ciudad.Pais.nombre if self.DireccionConsignar.Ciudad and self.DireccionConsignar.Ciudad.Pais else None,
                    "fono_1": self.DireccionConsignar.fono_1,
                }
            except:
                result["direccion_consignar"] = None
        else:
            result["direccion_consignar"] = None
        
        # Add notification address snapshots (with fallback)
        if self.direccion_notificar_texto:
            result["direccion_notificar"] = {
                "texto": self.direccion_notificar_texto,
                "ciudad": self.direccion_notificar_ciudad,
                "pais": self.direccion_notificar_pais,
                "fono_1": self.direccion_notificar_fono_1,
            }
        elif self.DireccionNotificar and hasattr(self.DireccionNotificar, 'direccion'):
            # Fallback to current direccion data
            try:
                result["direccion_notificar"] = {
                    "texto": self.DireccionNotificar.direccion,
                    "ciudad": self.DireccionNotificar.Ciudad.nombre if self.DireccionNotificar.Ciudad else None,
                    "pais": self.DireccionNotificar.Ciudad.Pais.nombre if self.DireccionNotificar.Ciudad and self.DireccionNotificar.Ciudad.Pais else None,
                    "fono_1": self.DireccionNotificar.fono_1,
                }
            except:
                result["direccion_notificar"] = None
        else:
            result["direccion_notificar"] = None
        
        return result

# (opcional) emula el beforeSave de Yii para id_proforma = max+1 (con mínimo 1798)
@event.listens_for(Proforma, "before_insert")
def proforma_before_insert(mapper, connection, target):
    if target.id_proforma is None:
        max_id = connection.execute(select(func.coalesce(func.max(Proforma.id_proforma), 0))).scalar_one()
        target.id_proforma = max(max_id + 1, 1798)


# Populate snapshot fields automatically when creating a proforma
@event.listens_for(Proforma, "before_insert")
def populate_proforma_snapshots(mapper, connection, target):
    """
    Automatically populate snapshot fields when creating a proforma.
    Captures immutable copies of empresa and direccion data at creation time.
    """
    # Import models here to avoid circular imports
    from app.models.empresa import Empresa
    from app.models.direccion import Direccion
    from app.models.ciudad import Ciudad
    from app.models.pais import Pais
    
    try:
        # Populate empresa snapshots
        if target.id_empresa:
            empresa_stmt = select(Empresa).where(Empresa.id_empresa == target.id_empresa)
            empresa = connection.execute(empresa_stmt).scalar_one_or_none()
            if empresa:
                target.empresa_nombre_fantasia = empresa.nombre_fantasia
                target.empresa_razon_social = empresa.razon_social
                target.empresa_rut = empresa.rut
                target.empresa_direccion = empresa.direccion
                target.empresa_giro = empresa.giro
    except Exception as e:
        print(f"Error populating empresa snapshot: {e}")
        pass
    
    try:
        # Populate billing address snapshots
        if target.id_direccion_facturar:
            dir_stmt = select(Direccion, Ciudad, Pais).join(
                Ciudad, Direccion.id_ciudad == Ciudad.id_ciudad
            ).join(
                Pais, Ciudad.id_pais == Pais.id_pais
            ).where(Direccion.id_direccion == target.id_direccion_facturar)
            
            result = connection.execute(dir_stmt).first()
            if result:
                direccion, ciudad, pais = result
                target.direccion_facturar_texto = direccion.direccion
                target.direccion_facturar_ciudad = ciudad.nombre
                target.direccion_facturar_pais = pais.nombre
                target.direccion_facturar_fono_1 = direccion.fono_1
    except Exception as e:
        print(f"Error populating facturar address snapshot: {e}")
        pass
    
    try:
        # Populate consignment address snapshots
        if target.id_direccion_consignar:
            dir_stmt = select(Direccion, Ciudad, Pais).join(
                Ciudad, Direccion.id_ciudad == Ciudad.id_ciudad
            ).join(
                Pais, Ciudad.id_pais == Pais.id_pais
            ).where(Direccion.id_direccion == target.id_direccion_consignar)
            
            result = connection.execute(dir_stmt).first()
            if result:
                direccion, ciudad, pais = result
                target.direccion_consignar_texto = direccion.direccion
                target.direccion_consignar_ciudad = ciudad.nombre
                target.direccion_consignar_pais = pais.nombre
                target.direccion_consignar_fono_1 = direccion.fono_1
    except Exception as e:
        print(f"Error populating consignar address snapshot: {e}")
        pass
    
    try:
        # Populate notification address snapshots
        if target.id_direccion_notificar:
            dir_stmt = select(Direccion, Ciudad, Pais).join(
                Ciudad, Direccion.id_ciudad == Ciudad.id_ciudad
            ).join(
                Pais, Ciudad.id_pais == Pais.id_pais
            ).where(Direccion.id_direccion == target.id_direccion_notificar)
            
            result = connection.execute(dir_stmt).first()
            if result:
                direccion, ciudad, pais = result
                target.direccion_notificar_texto = direccion.direccion
                target.direccion_notificar_ciudad = ciudad.nombre
                target.direccion_notificar_pais = pais.nombre
                target.direccion_notificar_fono_1 = direccion.fono_1
    except Exception as e:
        print(f"Error populating notificar address snapshot: {e}")
        pass


# Protect snapshot immutability - prevent updates to snapshot fields
@event.listens_for(Proforma, "before_update")
def protect_proforma_snapshots(mapper, connection, target):
    """
    Ensure snapshot fields remain immutable after creation.
    Restores original snapshot values even if update attempts to change them.
    """
    # Get the current state from the session
    state = target._sa_instance_state
    
    # List of all snapshot field names
    snapshot_fields = [
        'empresa_nombre_fantasia', 'empresa_razon_social', 'empresa_rut', 
        'empresa_direccion', 'empresa_giro',
        'direccion_facturar_texto', 'direccion_facturar_ciudad', 
        'direccion_facturar_pais', 'direccion_facturar_fono_1',
        'direccion_consignar_texto', 'direccion_consignar_ciudad',
        'direccion_consignar_pais', 'direccion_consignar_fono_1',
        'direccion_notificar_texto', 'direccion_notificar_ciudad',
        'direccion_notificar_pais', 'direccion_notificar_fono_1',
    ]
    
    # Check if any snapshot fields have been modified
    history = state.get_history('empresa_nombre_fantasia', True)
    if history.has_changes():
        # If snapshots are being modified, restore original values from database
        from sqlalchemy import select
        original_stmt = select(Proforma).where(Proforma.id_proforma == target.id_proforma)
        original = connection.execute(original_stmt).scalar_one_or_none()
        
        if original:
            # Restore all snapshot fields to their original values
            for field in snapshot_fields:
                setattr(target, field, getattr(original, field))
