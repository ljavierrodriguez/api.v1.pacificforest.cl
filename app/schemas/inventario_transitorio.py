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


class EntradaServicioDetalle(BaseModel):
    id_guia_servicio: Optional[int] = None
    id_orden_servicio: Optional[int] = None
    numero_guia_servicio: Optional[str] = None
    fecha: Optional[str] = None
    tipo: str = "GUIA_COSTO_SERVICIO"
    proceso: Optional[str] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    volumen_utilizado: float = 0.0
    piezas_utilizadas: float = 0.0
    raw_oc: Optional[str] = None


class InventarioTransitorioRead(InventarioTransitorioBase):
    id_inventario_transitorio: int
    id_especie: Optional[int] = None
    producto_nombre: Optional[str] = None
    bodega_nombre: Optional[str] = None
    unidad_venta_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    volumen_utilizado: Optional[float] = 0.0
    piezas_utilizadas: Optional[float] = 0.0
    saldo_volumen: Optional[float] = None
    saldo_piezas: Optional[float] = None
    porcentaje_utilizado: Optional[float] = 0.0
    estado_consumo: Optional[str] = "DISPONIBLE"
    entradas_servicio: List[EntradaServicioDetalle] = []

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
    total_volumen_utilizado: Optional[float] = 0.0
    total_piezas_utilizadas: Optional[float] = 0.0
    total_saldo_volumen: Optional[float] = 0.0
    total_saldo_piezas: Optional[float] = 0.0
    porcentaje_utilizado: Optional[float] = 0.0
    estado_consumo: Optional[str] = "DISPONIBLE"
    entradas_servicio: List[EntradaServicioDetalle] = []
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


class DesgloseOCResponse(BaseModel):
    id_orden_compra: int
    proveedor_nombre: Optional[str] = None
    total_volumen: float = 0.0
    volumen_utilizado: float = 0.0
    saldo_volumen: float = 0.0
    total_piezas: float = 0.0
    piezas_utilizadas: float = 0.0
    saldo_piezas: float = 0.0
    items_count: int = 0
    costo_producto: float = 0.0
    porcentaje_utilizado: float = 0.0
    estado_consumo: str = "DISPONIBLE"
    guias_recepcion: List[str] = []
    guias_servicio: List[str] = []
    entradas_servicio: List[EntradaServicioDetalle] = []


class ResumenInventarioTransitorioResponse(BaseModel):
    total_volumen: float = 0.0
    total_volumen_eq: float = 0.0
    total_volumen_utilizado: float = 0.0
    total_saldo_volumen: float = 0.0
    total_piezas: float = 0.0
    total_piezas_utilizadas: float = 0.0
    total_saldo_piezas: float = 0.0
    porcentaje_utilizado: float = 0.0
    total_costo_producto: float = 0.0
    total_costo_utilizado: float = 0.0
    total_costo_saldo: float = 0.0
    total_flete: float = 0.0
    total_costo: float = 0.0
    total_items: int = 0
    total_paquetes: int = 0
    desglose_por_oc: List[DesgloseOCResponse] = []
    desglose_bodegas: List[dict] = []
    desglose_productos: List[dict] = []

