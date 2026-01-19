from sqlalchemy import Integer, String, ForeignKey, event, Column
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base


class DetalleProforma(Base):
    __tablename__ = "detalle_proforma"

    id_detalle_proforma = Column(Integer, primary_key=True, autoincrement=True)

    id_proforma = Column(Integer, ForeignKey("proforma.id_proforma"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"))
    id_unidad_venta = Column(Integer, ForeignKey("unidad_venta.id_unidad_venta"), nullable=False)

    texto_libre = Column(String(200))

    espesor = Column(String(20))
    id_unidad_medida_espesor = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    ancho = Column(String(20))
    id_unidad_medida_ancho = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    largo = Column(String(20))
    id_unidad_medida_largo = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"))

    piezas = Column(Integer)

    cantidad = Column(String(12), nullable=False)
    precio_unitario = Column(String(12), nullable=False)
    subtotal = Column(String(12), nullable=False)
    volumen = Column(String(12))
    volumen_eq = Column(String(12), nullable=False)
    precio_eq = Column(String(12), nullable=False)

    # Product snapshot fields (immutable historical data)
    producto_nombre_esp = Column(String(100))
    producto_nombre_ing = Column(String(100))
    producto_obs_calidad = Column(String(2000))
    producto_especie = Column(String(100))

    Proforma = relationship(
        "Proforma",
        primaryjoin="foreign(DetalleProforma.id_proforma)==Proforma.id_proforma",
        back_populates="DetalleProforma",
    )
    Producto = relationship(
        "Producto",
        foreign_keys=[id_producto],
        viewonly=True,
    )
    UnidadVenta = relationship(
        "UnidadVenta",
        primaryjoin="foreign(DetalleProforma.id_unidad_venta)==UnidadVenta.id_unidad_venta",
        viewonly=True,
    )
    UnidadMedidaEspesor = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleProforma.id_unidad_medida_espesor)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaAncho = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleProforma.id_unidad_medida_ancho)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )
    UnidadMedidaLargo = relationship(
        "UnidadMedida",
        primaryjoin="foreign(DetalleProforma.id_unidad_medida_largo)==UnidadMedida.id_unidad_medida",
        viewonly=True,
    )

    def __repr__(self):
        return f"<DetalleProforma {self.id_detalle_proforma}>"

    def to_dict(self):
        result = {
            "id_detalle_proforma": self.id_detalle_proforma,
            "id_proforma": self.id_proforma,
            "id_producto": self.id_producto,
            "id_unidad_venta": self.id_unidad_venta,
            "texto_libre": self.texto_libre,
            "espesor": self.espesor,
            "id_unidad_medida_espesor": self.id_unidad_medida_espesor,
            "ancho": self.ancho,
            "id_unidad_medida_ancho": self.id_unidad_medida_ancho,
            "largo": self.largo,
            "id_unidad_medida_largo": self.id_unidad_medida_largo,
            "piezas": self.piezas,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": self.subtotal,
            "volumen": self.volumen,
            "volumen_eq": self.volumen_eq,
            "precio_eq": self.precio_eq,
        }
        
        # Include product snapshot data (with fallback to current Producto)
        if self.producto_nombre_esp:
            # Use snapshot data (prioritize historical accuracy)
            result["producto_snapshot"] = {
                "nombre_esp": self.producto_nombre_esp,
                "nombre_ing": self.producto_nombre_ing,
                "obs_calidad": self.producto_obs_calidad,
                "especie": self.producto_especie,
            }
        elif self.Producto is not None:
            # Fallback to current producto data for backward compatibility
            result["producto_snapshot"] = {
                "nombre_esp": self.Producto.nombre_producto_esp,
                "nombre_ing": self.Producto.nombre_producto_ing,
                "obs_calidad": self.Producto.obs_calidad,
                "especie": self.Producto.Especie.nombre_esp if self.Producto.Especie else None,
            }
        else:
            result["producto_snapshot"] = None
        
        # Keep legacy producto field for backward compatibility
        if self.Producto is not None:
            result["producto"] = {
                "id_producto": self.Producto.id_producto,
                "nombre_producto_esp": self.Producto.nombre_producto_esp,
                "nombre_producto_ing": self.Producto.nombre_producto_ing,
                "obs_calidad": self.Producto.obs_calidad,
            }
        else:
            result["producto"] = None
            
        return result



# Populate product snapshot fields automatically when creating a detalle_proforma
@event.listens_for(DetalleProforma, "before_insert")
def populate_detalle_snapshots(mapper, connection, target):
    """
    Automatically populate product snapshot fields when creating a detalle_proforma.
    Captures immutable copies of producto data at creation time.
    """
    from app.models.producto import Producto
    from app.models.especie import Especie
    
    if target.id_producto:
        # Access session from target's state to query ORM objects
        session = target._sa_instance_state.session
        if session:
            producto = session.get(Producto, target.id_producto)
            
            if producto:
                target.producto_nombre_esp = producto.nombre_producto_esp
                target.producto_nombre_ing = producto.nombre_producto_ing
                target.producto_obs_calidad = producto.obs_calidad
                
                # Fetch especie if available
                if producto.id_especie:
                    especie = session.get(Especie, producto.id_especie)
                    if especie:
                        target.producto_especie = especie.nombre_esp


# Protect product snapshot immutability - prevent updates to snapshot fields
@event.listens_for(DetalleProforma, "before_update")
def protect_detalle_snapshots(mapper, connection, target):
    """
    Ensure product snapshot fields remain immutable after creation.
    Restores original snapshot values even if update attempts to change them.
    """
    # Get the current state from the session
    state = target._sa_instance_state
    
    # List of all product snapshot field names
    snapshot_fields = [
        'producto_nombre_esp', 'producto_nombre_ing', 
        'producto_obs_calidad', 'producto_especie'
    ]
    
    # Check if any snapshot fields have been modified
    history = state.get_history('producto_nombre_esp', True)
    if history.has_changes():
        # If snapshots are being modified, restore original values from database
        from sqlalchemy import select
        original_stmt = select(DetalleProforma).where(
            DetalleProforma.id_detalle_proforma == target.id_detalle_proforma
        )
        original = connection.execute(original_stmt).scalars().first()
        
        if original:
            # Restore all snapshot fields to their original values
            for field in snapshot_fields:
                setattr(target, field, getattr(original, field))


# ===== Hook equivalente a beforeValidate() de Yii =====
@event.listens_for(DetalleProforma, "before_insert")
@event.listens_for(DetalleProforma, "before_update")
def _round_vols(mapper, connection, target: DetalleProforma):
    def _round3_str(v):
        if v is None or str(v).strip() == "":
            return v
        try:
            n = round(float(str(v).replace(",", ".")), 3)
            s = f"{n:.3f}".rstrip("0").rstrip(".")
            return s
        except Exception:
            return v

    target.volumen_eq = _round3_str(target.volumen_eq)
    target.volumen = _round3_str(target.volumen)
