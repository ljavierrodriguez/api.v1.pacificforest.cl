from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date, event
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base
from datetime import date


class InventarioTransitorio(Base):
    __tablename__ = "inventario_transitorio"

    id_inventario_transitorio = Column(Integer, primary_key=True, autoincrement=True)
    id_guia_inventario_transitorio = Column(Integer, ForeignKey("guia_inventario_transitorio.id_guia_inventario_transitorio", ondelete="CASCADE"), nullable=True)

    id_orden_compra = Column(Integer, ForeignKey("orden_compra.id_orden_compra"), nullable=True)
    id_detalle_odc = Column(Integer, ForeignKey("detalle_orden_compra.id_detalle_odc"), nullable=True)
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
    numero_guia = Column(String(100), nullable=True)
    numero_proforma = Column(String(100), nullable=True)
    etiqueta = Column(String(100), nullable=True)
    numero_paquetes = Column(Integer, nullable=True)
    url_documento = Column(String(500), nullable=True)
    observaciones = Column(String(500), nullable=True)
    estado = Column(String(50), default="RECIBIDO")

    # Relaciones
    guia = relationship(
        "GuiaInventarioTransitorio",
        back_populates="detalles",
    )
    OrdenCompra = relationship(
        "OrdenCompra",
        primaryjoin="foreign(InventarioTransitorio.id_orden_compra)==OrdenCompra.id_orden_compra",
        viewonly=True,
    )
    DetalleOrdenCompra = relationship(
        "DetalleOrdenCompra",
        primaryjoin="foreign(InventarioTransitorio.id_detalle_odc)==DetalleOrdenCompra.id_detalle_odc",
        viewonly=True,
    )
    Producto = relationship(
        "Producto",
        primaryjoin="foreign(InventarioTransitorio.id_producto)==Producto.id_producto",
        viewonly=True,
    )
    Bodega = relationship(
        "Bodega",
        primaryjoin="foreign(InventarioTransitorio.id_bodega)==Bodega.id_bodega",
        viewonly=True,
    )
    UnidadVenta = relationship(
        "UnidadVenta",
        primaryjoin="foreign(InventarioTransitorio.id_unidad_venta)==UnidadVenta.id_unidad_venta",
        viewonly=True,
    )

    def __repr__(self):
        return f"<InventarioTransitorio {self.id_inventario_transitorio}>"

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
        oc = self.OrdenCompra
        if not oc and self.id_orden_compra:
            from sqlalchemy.orm import object_session
            sess = object_session(self)
            if sess:
                from app.models.orden_compra import OrdenCompra
                oc = sess.get(OrdenCompra, self.id_orden_compra)

        if oc and getattr(oc, "ClienteProveedor", None):
            proveedor_nombre = getattr(oc.ClienteProveedor, "razon_social", None)

        g = self.guia
        num_guia = self.numero_guia or (g.numero_guia if g else None)
        num_pf = self.numero_proforma or (g.numero_proforma if g else None)
        url_doc = self.url_documento or (g.url_documento if g else None)
        fecha_rec = self.fecha_recepcion or (g.fecha_recepcion if g else None)

        return {
            "id_inventario_transitorio": self.id_inventario_transitorio,
            "id_guia_inventario_transitorio": self.id_guia_inventario_transitorio,
            "id_orden_compra": self.id_orden_compra,
            "id_detalle_odc": self.id_detalle_odc,
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
            "fecha_recepcion": fecha_rec.isoformat() if hasattr(fecha_rec, "isoformat") else fecha_rec,
            "numero_guia": num_guia,
            "numero_proforma": num_pf,
            "etiqueta": self.etiqueta,
            "numero_paquetes": self.numero_paquetes,
            "url_documento": url_doc,
            "observaciones": self.observaciones,
            "estado": self.estado,
        }


@event.listens_for(InventarioTransitorio, "before_insert")
@event.listens_for(InventarioTransitorio, "before_update")
def _round_inv_vols(mapper, connection, target: InventarioTransitorio):
    def _round3(v):
        if v is None:
            return None
        try:
            return round(float(v), 3)
        except Exception:
            return v

    target.volumen_eq = _round3(target.volumen_eq)
    target.volumen = _round3(target.volumen)
