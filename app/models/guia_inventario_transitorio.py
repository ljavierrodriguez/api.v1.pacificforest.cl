from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import date


class GuiaInventarioTransitorio(Base):
    __tablename__ = "guia_inventario_transitorio"

    id_guia_inventario_transitorio = Column(Integer, primary_key=True, autoincrement=True)

    numero_guia = Column(String(100), nullable=True, index=True)
    numero_proforma = Column(String(100), nullable=True)
    id_orden_compra = Column(Integer, ForeignKey("orden_compra.id_orden_compra"), nullable=True)
    id_bodega = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=True)
    fecha_recepcion = Column(Date, default=date.today)
    url_documento = Column(String(500), nullable=True)
    observaciones = Column(String(500), nullable=True)
    estado = Column(String(50), default="RECIBIDO")

    # Relaciones viewonly / ORM
    OrdenCompra = relationship(
        "OrdenCompra",
        primaryjoin="foreign(GuiaInventarioTransitorio.id_orden_compra)==OrdenCompra.id_orden_compra",
        viewonly=True,
    )
    Bodega = relationship(
        "Bodega",
        primaryjoin="foreign(GuiaInventarioTransitorio.id_bodega)==Bodega.id_bodega",
        viewonly=True,
    )
    detalles = relationship(
        "InventarioTransitorio",
        back_populates="guia",
        cascade="all, delete-orphan",
        order_by="InventarioTransitorio.id_inventario_transitorio",
    )

    def __repr__(self):
        return f"<GuiaInventarioTransitorio {self.id_guia_inventario_transitorio} - Guia {self.numero_guia}>"

    def to_dict(self):
        bodega_nombre = getattr(self.Bodega, "nombre", None) if self.Bodega else None
        proveedor_nombre = None
        if self.OrdenCompra and getattr(self.OrdenCompra, "ClienteProveedor", None):
            proveedor_nombre = getattr(self.OrdenCompra.ClienteProveedor, "razon_social", None)

        detalles_list = [d.to_dict() for d in self.detalles] if self.detalles else []
        total_volumen = sum(d.get("volumen_eq") or d.get("volumen") or 0 for d in detalles_list)
        total_piezas = sum(d.get("piezas") or 0 for d in detalles_list)
        total_paquetes = sum(d.get("numero_paquetes") or 0 for d in detalles_list)

        return {
            "id_guia_inventario_transitorio": self.id_guia_inventario_transitorio,
            "numero_guia": self.numero_guia,
            "numero_proforma": self.numero_proforma,
            "id_orden_compra": self.id_orden_compra,
            "id_bodega": self.id_bodega,
            "bodega_nombre": bodega_nombre,
            "proveedor_nombre": proveedor_nombre,
            "fecha_recepcion": self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            "url_documento": self.url_documento,
            "observaciones": self.observaciones,
            "estado": self.estado,
            "total_volumen": round(total_volumen, 3),
            "total_piezas": total_piezas,
            "total_paquetes": total_paquetes,
            "detalles": detalles_list,
        }
