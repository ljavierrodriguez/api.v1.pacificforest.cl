from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal


class InventarioTransitorioBase(BaseModel):
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
    observaciones: Optional[str] = Field(None, max_length=500)
    estado: Optional[str] = Field("RECIBIDO", max_length=50)


class InventarioTransitorioCreate(InventarioTransitorioBase):
    pass


class InventarioTransitorioUpdate(BaseModel):
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
    observaciones: Optional[str] = None
    estado: Optional[str] = None


class RecepcionarItemPayload(BaseModel):
    id_detalle_odc: Optional[int] = None
    id_producto: Optional[int] = None
    cantidad: Optional[Decimal] = None
    piezas: Optional[Decimal] = None
    volumen: Optional[Decimal] = None
    volumen_eq: Optional[Decimal] = None
    id_bodega: Optional[int] = None
    observaciones: Optional[str] = None


class RecepcionarOrdenCompraPayload(BaseModel):
    id_bodega: Optional[int] = None
    fecha_recepcion: Optional[date] = None
    observaciones: Optional[str] = None
    items: Optional[List[RecepcionarItemPayload]] = None


class InventarioTransitorioRead(InventarioTransitorioBase):
    id_inventario_transitorio: int
    id_especie: Optional[int] = None
    producto_nombre: Optional[str] = None
    bodega_nombre: Optional[str] = None
    unidad_venta_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedInventarioTransitorioResponse(BaseModel):
    items: List[InventarioTransitorioRead]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
