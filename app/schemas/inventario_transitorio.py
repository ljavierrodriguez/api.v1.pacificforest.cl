from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal


class InventarioTransitorioBase(BaseModel):
    id_guia_inventario_transitorio: Optional[int] = None
    id_orden_compra: Optional[int] = None
    id_detalle_odc: Optional[int] = None
    id_producto: Optional[int] = None
    id_bodega: Optional[int] = None
    id_unidad_venta: Optional[int] = None
    texto_abierto: Optional[str] = Field(None, max_length=200)
    espesor: Optional[str] = Field(None, max_length=20)
    id_unidad_medida_espesor: Optional[int] = None
    ancho: Optional[str] = Field(None, max_length=20)
    id_unidad_medida_ancho: Optional[int] = None
    largo: Optional[str] = Field(None, max_length=20)
    id_unidad_medida_largo: Optional[int] = None
    cantidad: Optional[Decimal] = None
    precio_unitario: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None
    volumen: Optional[Decimal] = None
    volumen_eq: Optional[Decimal] = None
    precio_eq: Optional[Decimal] = None
    piezas: Optional[Decimal] = None
    fecha_recepcion: Optional[date] = None
    numero_guia: Optional[str] = Field(None, max_length=100)
    numero_proforma: Optional[str] = Field(None, max_length=100)
    etiqueta: Optional[str] = Field(None, max_length=100)
    numero_paquetes: Optional[int] = None
    url_documento: Optional[str] = Field(None, max_length=500)
    observaciones: Optional[str] = Field(None, max_length=500)
    estado: Optional[str] = Field("RECIBIDO", max_length=50)


class InventarioTransitorioCreate(InventarioTransitorioBase):
    pass


class InventarioTransitorioUpdate(BaseModel):
    id_guia_inventario_transitorio: Optional[int] = None
    id_orden_compra: Optional[int] = None
    id_detalle_odc: Optional[int] = None
    id_producto: Optional[int] = None
    id_bodega: Optional[int] = None
    id_unidad_venta: Optional[int] = None
    texto_abierto: Optional[str] = None
    espesor: Optional[str] = None
    id_unidad_medida_espesor: Optional[int] = None
    ancho: Optional[str] = None
    id_unidad_medida_ancho: Optional[int] = None
    largo: Optional[str] = None
    id_unidad_medida_largo: Optional[int] = None
    cantidad: Optional[Decimal] = None
    precio_unitario: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None
    volumen: Optional[Decimal] = None
    volumen_eq: Optional[Decimal] = None
    precio_eq: Optional[Decimal] = None
    piezas: Optional[Decimal] = None
    fecha_recepcion: Optional[date] = None
    numero_guia: Optional[str] = None
    numero_proforma: Optional[str] = None
    etiqueta: Optional[str] = None
    numero_paquetes: Optional[int] = None
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None


class RecepcionarItemPayload(BaseModel):
    id_detalle_odc: Optional[int] = None
    id_producto: Optional[int] = None
    texto_abierto: Optional[str] = None
    espesor: Optional[str] = None
    ancho: Optional[str] = None
    largo: Optional[str] = None
    cantidad: Optional[Decimal] = None
    piezas: Optional[Decimal] = None
    volumen: Optional[Decimal] = None
    volumen_eq: Optional[Decimal] = None
    id_bodega: Optional[int] = None
    numero_guia: Optional[str] = None
    numero_proforma: Optional[str] = None
    etiqueta: Optional[str] = None
    numero_paquetes: Optional[int] = None
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None


class RecepcionarGuiaPayload(BaseModel):
    numero_guia: Optional[str] = None
    fecha_recepcion: Optional[date] = None
    id_bodega: Optional[int] = None
    numero_proforma: Optional[str] = None
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None
    items: Optional[List[RecepcionarItemPayload]] = None


class RecepcionarOrdenCompraPayload(BaseModel):
    id_bodega: Optional[int] = None
    fecha_recepcion: Optional[date] = None
    numero_guia: Optional[str] = None
    numero_proforma: Optional[str] = None
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None
    items: Optional[List[RecepcionarItemPayload]] = None
    guias: Optional[List[RecepcionarGuiaPayload]] = None


class InventarioTransitorioRead(InventarioTransitorioBase):
    id_inventario_transitorio: int
    id_especie: Optional[int] = None
    producto_nombre: Optional[str] = None
    bodega_nombre: Optional[str] = None
    unidad_venta_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GuiaInventarioTransitorioRead(BaseModel):
    id_guia_inventario_transitorio: int
    numero_guia: Optional[str] = None
    numero_proforma: Optional[str] = None
    id_orden_compra: Optional[int] = None
    id_bodega: Optional[int] = None
    bodega_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    fecha_recepcion: Optional[date] = None
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None
    total_volumen: Optional[float] = 0.0
    total_piezas: Optional[float] = 0.0
    total_paquetes: Optional[int] = 0
    detalles: List[InventarioTransitorioRead] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedGuiaInventarioTransitorioResponse(BaseModel):
    items: List[GuiaInventarioTransitorioRead]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedInventarioTransitorioResponse(BaseModel):
    items: List[InventarioTransitorioRead]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
