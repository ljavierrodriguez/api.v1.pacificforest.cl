from datetime import date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class DetalleCostoServicioBase(BaseModel):
    servicio: str = Field(..., max_length=200)
    volumen_m3: Optional[Decimal] = None
    tarifa_usd_m3: Optional[Decimal] = None
    total_usd: Optional[Decimal] = None


class DetalleCostoServicioCreate(DetalleCostoServicioBase):
    pass


class DetalleCostoServicioRead(DetalleCostoServicioBase):
    id_detalle_costo_servicio: int
    id_guia_costo_servicio: int

    model_config = ConfigDict(from_attributes=True)


class GuiaCostoProductoTerminadoBase(BaseModel):
    espesor: Optional[Decimal] = None
    ancho: Optional[Decimal] = None
    largo: Optional[Decimal] = None
    piezas: Optional[int] = None
    volumen_m3: Optional[Decimal] = None


class GuiaCostoProductoTerminadoCreate(GuiaCostoProductoTerminadoBase):
    pass


class GuiaCostoProductoTerminadoRead(GuiaCostoProductoTerminadoBase):
    id_producto_terminado: int
    id_guia_costo_servicio: int

    model_config = ConfigDict(from_attributes=True)


class GuiaCostoDetalleProcesoBase(BaseModel):
    origen_entrada: Optional[str] = None
    estado_entrada: Optional[str] = None
    planta_secado: Optional[str] = None
    planta_cepillado: Optional[str] = None
    oc_compra_entrada: Optional[str] = None
    espesor_entrada: Optional[Decimal] = None
    ancho_entrada: Optional[Decimal] = None
    largo_entrada: Optional[Decimal] = None
    piezas_entrada: Optional[int] = None
    volumen_m3_entrada: Optional[Decimal] = None

    espesor_salida: Optional[Decimal] = None
    ancho_salida: Optional[Decimal] = None
    largo_salida: Optional[Decimal] = None
    piezas_salida: Optional[int] = None
    volumen_m3_salida: Optional[Decimal] = None
    proceso: Optional[str] = None


class GuiaCostoDetalleProcesoCreate(GuiaCostoDetalleProcesoBase):
    pass


class GuiaCostoDetalleProcesoRead(GuiaCostoDetalleProcesoBase):
    id_detalle_proceso: int
    id_guia_costo_servicio: int

    model_config = ConfigDict(from_attributes=True)


class GuiaCostoServicioCreate(BaseModel):
    numero_guia: str = Field(..., max_length=100)
    fecha_despacho: Optional[date] = None
    origen: Optional[str] = None
    producto: Optional[str] = None
    destino: Optional[str] = None
    oc_compra_ref: Optional[str] = None
    total_m3: Optional[Decimal] = None
    total_usd: Optional[Decimal] = None
    observaciones: Optional[str] = None
    url_documento: Optional[str] = None
    ordenes_servicio_ids: Optional[List[int]] = None
    ordenes_compra_ids: Optional[List[int]] = None
    detalles: Optional[List[DetalleCostoServicioCreate]] = None
    productos_terminados: Optional[List[GuiaCostoProductoTerminadoCreate]] = None
    detalles_proceso: Optional[List[GuiaCostoDetalleProcesoCreate]] = None


class BatchGuiaCostoServicioCreate(BaseModel):
    guias: List[GuiaCostoServicioCreate]


class GuiaCostoServicioRead(BaseModel):
    id_guia_costo_servicio: int
    numero_guia: str
    fecha_despacho: Optional[date] = None
    fecha_registro: Optional[date] = None
    origen: Optional[str] = None
    producto: Optional[str] = None
    destino: Optional[str] = None
    oc_compra_ref: Optional[str] = None
    total_m3: Optional[float] = None
    total_usd: Optional[float] = None
    observaciones: Optional[str] = None
    url_documento: Optional[str] = None
    ordenes_servicio_ids: List[int] = []
    ordenes_compra_ids: List[int] = []
    detalles: List[DetalleCostoServicioRead] = []
    productos_terminados: List[GuiaCostoProductoTerminadoRead] = []
    detalles_proceso: List[GuiaCostoDetalleProcesoRead] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedGuiaCostoServicioResponse(BaseModel):
    total_items: int
    total_pages: int
    page: int
    page_size: int
    items: List[GuiaCostoServicioRead]
