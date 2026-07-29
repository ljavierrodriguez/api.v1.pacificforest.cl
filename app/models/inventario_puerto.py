from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base
from datetime import date


class InventarioPuerto(Base):
    __tablename__ = "inventario_puerto"

    id_inventario_puerto = Column(Integer, primary_key=True, autoincrement=True)

    id_orden_servicio = Column(Integer, ForeignKey("orden_servicio.id_orden_servicio"), nullable=True)
    id_detalle_os = Column(Integer, ForeignKey("detalle_orden_servicio.id_detalle_os"), nullable=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=True)
    id_bodega = Column(Integer, ForeignKey("bodega.id_bodega"), nullable=True)
    id_unidad_venta = Column(Integer, ForeignKey("unidad_venta.id_unidad_venta"), nullable=True)

    texto_abierto = Column(String(200), nullable=True)

    espesor = Column(String(20), nullable=True)
    id_unidad_medida_espesor = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=True)

    ancho = Column(String(20), nullable=True)
    id_unidad_medida_ancho = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=True)

    largo = Column(String(20), nullable=True)
    id_unidad_medida_largo = Column(Integer, ForeignKey("unidad_medida.id_unidad_medida"), nullable=True)

    cantidad = Column(Numeric(12, 3), nullable=True)
    precio_unitario = Column(Numeric(12, 3), nullable=True)
    subtotal = Column(Numeric(12, 3), nullable=True)

    volumen = Column(Numeric(12, 3), nullable=True)
    volumen_eq = Column(Numeric(12, 3), nullable=True)
    precio_eq = Column(Numeric(12, 3), nullable=True)
    piezas = Column(Numeric(12, 3), nullable=True)

    fecha_recepcion = Column(Date, default=date.today)
    observaciones = Column(String(500), nullable=True)
    estado = Column(String(50), default="RECIBIDO")

    # Relaciones viewonly
    OrdenServicio = relationship(
        "OrdenServicio",
        primaryjoin="foreign(InventarioPuerto.id_orden_servicio)==OrdenServicio.id_orden_servicio",
        viewonly=True,
    )
    DetalleOrdenServicio = relationship(
        "DetalleOrdenServicio",
        primaryjoin="foreign(InventarioPuerto.id_detalle_os)==DetalleOrdenServicio.id_detalle_os",
        viewonly=True,
    )
    Producto = relationship(
        "Producto",
        primaryjoin="foreign(InventarioPuerto.id_producto)==Producto.id_producto",
        viewonly=True,
    )
    Bodega = relationship(
        "Bodega",
        primaryjoin="foreign(InventarioPuerto.id_bodega)==Bodega.id_bodega",
        viewonly=True,
    )
    UnidadVenta = relationship(
        "UnidadVenta",
        primaryjoin="foreign(InventarioPuerto.id_unidad_venta)==UnidadVenta.id_unidad_venta",
        viewonly=True,
    )

    def __repr__(self):
        return f"<InventarioPuerto {self.id_inventario_puerto}>"

    def to_dict(self):
        def _num(x):
            return float(x) if x is not None else None

        prod = self.Producto
        if not prod and self.id_producto:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.producto import Producto
                prod = sess.get(Producto, self.id_producto)

        prod_nombre = None
        id_especie = None
        if prod:
            prod_nombre = getattr(prod, "nombre_producto_esp", None) or getattr(prod, "nombre", None) or getattr(prod, "nombre_producto_ing", None)
            id_especie = getattr(prod, "id_especie", None)

        uv = self.UnidadVenta
        if not uv and self.id_unidad_venta:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.unidad_venta import UnidadVenta
                uv = sess.get(UnidadVenta, self.id_unidad_venta)

        uv_nombre = getattr(uv, "nombre", None) if uv else None

        bodega = self.Bodega
        if not bodega and self.id_bodega:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.bodega import Bodega
                bodega = sess.get(Bodega, self.id_bodega)

        bodega_nombre = getattr(bodega, "nombre", None) if bodega else None

        proveedor_nombre = None
        os = self.OrdenServicio
        if not os and self.id_orden_servicio:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.orden_servicio import OrdenServicio
                os = sess.get(OrdenServicio, self.id_orden_servicio)

        if os and getattr(os, "ClienteProveedor", None):
            proveedor_nombre = getattr(os.ClienteProveedor, "razon_social", None)

        return {
            "id_inventario_puerto": self.id_inventario_puerto,
            "id_orden_servicio": self.id_orden_servicio,
            "id_detalle_os": self.id_detalle_os,
            "id_producto": self.id_producto,
            "id_especie": id_especie,
            "producto_nombre": prod_nombre,
            "id_bodega": self.id_bodega,
            "bodega_nombre": bodega_nombre,
            "proveedor_nombre": proveedor_nombre,
            "texto_abierto": self.texto_abierto,
            "id_unidad_venta": self.id_unidad_venta,
            "unidad_venta_nombre": uv_nombre,
            "cantidad": _num(self.cantidad),
            "espesor": self.espesor,
            "id_unidad_medida_espesor": self.id_unidad_medida_espesor,
            "ancho": self.ancho,
            "id_unidad_medida_ancho": self.id_unidad_medida_ancho,
            "largo": self.largo,
            "id_unidad_medida_largo": self.id_unidad_medida_largo,
            "precio_unitario": _num(self.precio_unitario),
            "subtotal": _num(self.subtotal),
            "volumen": _num(self.volumen),
            "volumen_eq": _num(self.volumen_eq),
            "precio_eq": _num(self.precio_eq),
            "piezas": _num(self.piezas),
            "fecha_recepcion": self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            "observaciones": self.observaciones,
            "estado": self.estado,
        }
