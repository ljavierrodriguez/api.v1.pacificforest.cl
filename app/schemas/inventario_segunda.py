from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.guia_costo_servicio import (
    DetalleCostoServicioRead,
    GuiaCostoDetalleProcesoRead,
)


class ItemStockSegunda(BaseModel):
    id_stock_planta: Optional[int] = None
    id_guia_costo_servicio: int
    numero_guia: str
    fecha_despacho: Optional[date] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    producto: Optional[str] = None
    oc_compra_ref: Optional[str] = None
    espesor: Optional[float] = None
    ancho: Optional[float] = None
    largo: Optional[float] = None
    piezas: Optional[int] = None
    volumen_m3: Optional[float] = None
    tipo_stock: Optional[str] = "2da"
    costo_madera_m3: Optional[float] = None
    servicios_m3: Optional[float] = None
    costo_final_unitario: Optional[float] = None
    costo_final_total: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ItemResumenSegunda(BaseModel):
    id_resumen_general: int
    id_guia_costo_servicio: int
    oc_tabla: Optional[str] = None
    movimiento: Optional[str] = None
    volumen_m3: Optional[float] = None
    estado: Optional[str] = None
    costo_madera_m3: Optional[float] = None
    servicios_m3: Optional[float] = None
    costo_final_unitario: Optional[float] = None
    costo_madera_total: Optional[float] = None
    costo_servicios_total: Optional[float] = None
    costo_final_total: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class GuiaInventarioSegundaRead(BaseModel):
    id_guia_costo_servicio: int
    numero_guia: str
    fecha_despacho: Optional[date] = None
    fecha_registro: Optional[date] = None
    origen: Optional[str] = None
    destino: Optional[str] = None
    producto: Optional[str] = None
    oc_compra_ref: Optional[str] = None
    flejes_2da: Optional[float] = None
    total_volumen_2da: float = 0.0
    total_piezas_2da: int = 0
    total_costo_madera_2da: float = 0.0
    total_servicios_2da: float = 0.0
    total_costo_final_2da: float = 0.0
    costo_promedio_2da_m3: float = 0.0
    url_documento: Optional[str] = None
    observaciones: Optional[str] = None
    ordenes_compra_ids: List[int] = []
    ordenes_servicio_ids: List[int] = []
    stock_planta_2da: List[ItemStockSegunda] = []
    resumen_general_2da: List[ItemResumenSegunda] = []
    servicios: List[DetalleCostoServicioRead] = []
    detalles_proceso: List[GuiaCostoDetalleProcesoRead] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedGuiaInventarioSegundaResponse(BaseModel):
    total_items: int
    total_pages: int
    page: int
    page_size: int
    items: List[GuiaInventarioSegundaRead]


class PaginatedItemInventarioSegundaResponse(BaseModel):
    total_items: int
    total_pages: int
    page: int
    page_size: int
    items: List[ItemStockSegunda]


class DesgloseOrigenSegunda(BaseModel):
    origen: str
    total_m3: float
    total_piezas: int
    guias_count: int
    total_costo_usd: float = 0.0
    costo_promedio_m3: float = 0.0


class DesgloseDimensionSegunda(BaseModel):
    dimension: str
    espesor: Optional[float] = None
    ancho: Optional[float] = None
    largo: Optional[float] = None
    total_piezas: int
    total_m3: float
    total_costo_usd: float = 0.0
    costo_promedio_m3: float = 0.0


class DesgloseMensualSegunda(BaseModel):
    mes_anio: str
    total_m3: float
    total_piezas: int
    guias_count: int
    total_costo_usd: float = 0.0
    costo_promedio_m3: float = 0.0


class StatsInventarioSegundaResponse(BaseModel):
    total_volumen_2da_m3: float
    total_piezas_2da: int
    total_guias_con_2da: int
    total_origenes: int
    total_costo_final_2da: float = 0.0
    costo_promedio_2da_m3: float = 0.0
    desglose_por_origen: List[DesgloseOrigenSegunda] = []
    desglose_por_dimension: List[DesgloseDimensionSegunda] = []
    desglose_mensual: List[DesgloseMensualSegunda] = []
